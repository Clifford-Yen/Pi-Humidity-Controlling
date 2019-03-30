import sqlite3
import Adafruit_DHT
import numpy
import time

def getMean(data, withStd=False, removeOutlier=False):
    ''' data should be a list. '''
    elements = numpy.array(data)
    mean = numpy.mean(elements, axis = 0)
    std = numpy.std(elements, axis = 0)
    if removeOutlier:
        for i in range(len(mean)):
            if std[i] > 1e-3:
                data = [x for x in data if (x[i] > mean[i] - 2*std[i]) and (x[i] < mean[i] + 2*std[i])]
        mean, std = getMean(data, withStd=True)
    if withStd:
        return mean, std
    else:
        return mean

def getTempHumidity(sensor, pin, interval=2, unit='C'):
    fails = 0
    humidity, temperature = None, None
    while humidity is None and temperature is None:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
            if unit[0] == 'F': # if you wish to use Fahrenheit
                temperature = temperature * 9/5.0 + 32
            return temperature, humidity
        else:
            fails += 1
            if fails >= 2:
                raise ValueError('The sensor keep failing to read the temperature and humidity.')
            time.sleep(interval)

def getTempHumidityMean(sensor, pin, sampleNum=20, interval=2):
    data = []
    while len(data) < sampleNum:
        time.sleep(interval)
        data.append(getTempHumidity(sensor, pin))
    mean = getMean(data, removeOutlier=True)
    temperature = mean[0]
    humidity = mean[1]
    return temperature, humidity

def log_values(db_path, sensor, pin):
    # It is important to provide an absolute path to the database file, otherwise Cron won't be able to find it!
    with sqlite3.connect(db_path) as conn:
        temperature, humidity = getTempHumidityMean(sensor, pin)
        # print('Temperature={0:0.1f}*  Humidity={1:0.1f}%'.format(temperature, humidity))
        curs = conn.cursor()
        curs.execute("""INSERT INTO log values((?), datetime(CURRENT_TIMESTAMP, 'localtime'), (?), (?))""", (curs.lastrowid, temperature, humidity))
        conn.commit()

if __name__ == '__main__':
    sensor = Adafruit_DHT.AM2302
    pin = 21
    log_values('/home/pi/HumidityControlling/TempHumidity.db', sensor, pin)