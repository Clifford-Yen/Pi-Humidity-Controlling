import sqlite3
import subprocess
from datetime import datetime, timedelta
from env_log import getMean
from TempHumidityMonitor import sendControl, get_records, get_datetime_string_hours_before as gts

def turnAircon(db_path, status_now=None, ecoLock={'humidity': True, 'temperature': True}, 
    windowProtection=False, leastExpectedImprovement=0.03, recentHour=1, previousHour=2, stopHour=17, 
    humidityLimit={'high': 65.0, 'low': 55.0}, tempLimit={'high': 21.0, 'low': 19.0}):
    data = {
        'current': {'tick': recentHour, 'tock': 0},
        'previous': {'tick': previousHour, 'tock': recentHour}
    }
    for key, options in data.items():
        logs = get_records(from_date_str=gts(options['tick']), to_date_str=gts(options['tock']))
        mean = getMean([[x[2], x[3]] for x in logs], removeOutlier=True)
        data[key].update({'temperature': mean[0], 'humidity': mean[1]})
        print('The '+key+' temperature is '+str(mean[0])+', and the '+key+' humidity is '+str(mean[1]))
    
    with sqlite3.connect(db_path) as conn:
        curs = conn.cursor()
        curs.execute("""SELECT * FROM log ORDER BY id DESC LIMIT 1""")
        logs = curs.fetchall()
        timeStamp = datetime.strptime(logs[0][1], "%Y-%m-%d %H:%M:%S")
        if status_now is None:
            status_now = logs[0][2]
        status = None
        ecoProtection = False
        # property is a reserved word in Python, so...
        for propertyName in ecoLock.keys():
            if ecoLock[propertyName] and data['current'][propertyName] > data['previous'][propertyName] * (1.0 - leastExpectedImprovement):
                ecoProtection = True
        if status_now == 'on' and ecoProtection:
            status = sendControl('off')
            print('The humidity or temperature is not lower after turning on the aircon. Please check.')
            if windowProtection:
                status = 'error'
                print('(Maybe the window is not closed?)')
        elif datetime.now() > datetime.now().replace(hour=stopHour, minute=0):
            if status_now == 'on':
                status = sendControl('off')
                print("It's "+str(stopHour)+" o'clock. Turn off the aircon.")
        elif status_now == 'off' and data['current']['humidity'] > humidityLimit['high'] and data['current']['temperature'] > tempLimit['high']:
            status = sendControl('dehumidify_on')
            print('Turn on the aircon.')
        elif status_now == 'on' and (data['current']['humidity'] < humidityLimit['low'] or data['current']['temperature'] < tempLimit['low']):
            status = sendControl('off')
            print('Turn off the aircon.')
        elif status_now in ['error', 'ventilation'] and datetime.now() - timeStamp >= timedelta(hours=12):
            print('Reset the error yesterday.')
            turnAircon(db_path, status_now='off')

        if status is not None:
            curs.execute("""INSERT INTO log values((?), datetime(CURRENT_TIMESTAMP, 'localtime'), (?))""", (curs.lastrowid, status))
            conn.commit()

if __name__ == '__main__':
    db_path = '/home/pi/HumidityControlling/aircon.db'
    turnAircon(db_path)