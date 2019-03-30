from flask import Flask, request, render_template, jsonify
import time
from datetime import datetime, timedelta
import Adafruit_DHT
import sqlite3
import re
import subprocess
from env_log import getTempHumidity
app = Flask(__name__)
app.debug = True # Make this False if you are no longer debugging
sensor = Adafruit_DHT.AM2302
pin = 21
tempHumidity_db_path = '/home/pi/HumidityControlling/TempHumidity.db'
aircon_db_path = '/home/pi/HumidityControlling/aircon.db'

@app.route("/")
def tempHumidity():
    temperature, humidity = getTempHumidity(sensor, pin)
    return render_template("tempHumidity.html", temp=temperature, hum=humidity)

@app.route("/env_db", methods=['GET'])  # Add date limits in the URL # Arguments: from=2015-03-04&to=2015-03-05
def env_db():
    logs, from_date_str, to_date_str = get_records()
    # reformated_logs = [re.split('-| |:', x[1])+[x[2], x[3]] for x in logs]
    reformated_logs = [[*re.split('-| |:', x[1]), x[2], x[3]] for x in logs]
    if len(reformated_logs) >= 1:
        updated_logs = appendAirconStatus(reformated_logs)
        return render_template("env_db.html", logs = updated_logs, 
            from_date = from_date_str, to_date = to_date_str,
            query_string = request.query_string)
    else:
        return render_template("no_record.html")

@app.route("/turnAircon", methods=['POST'])
def turnAircon():
    operation = request.form.get('operation', None)
    if operation is not None:
        status = sendControl(operation)
        with sqlite3.connect(aircon_db_path) as conn:
            curs = conn.cursor()
            curs.execute("""INSERT INTO log values((?), datetime(CURRENT_TIMESTAMP, 'localtime'), (?))""", (curs.lastrowid, status))
            conn.commit()
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'failed'})

def sendControl(operation, remoteName='SAMPO_AirCon'):
    """ Do irrecord on your Raspberry Pi first and replace the remote and operation name here.
    My operation can be 'off', 'dehumidify_on' and 'ventilation_on'. """
    subprocess.call(['irsend', 'SEND_ONCE', remoteName, operation])
    statusTable = {
        'ventilation_on': 'ventilation',
        'dehumidify_on': 'on',
        'off': 'off'
    }
    return statusTable[operation]

def get_datetime_string_hours_before(hr):
    targetTime = datetime.now() - timedelta(hours=hr)
    return datetime.strftime(targetTime, "%Y-%m-%d %H:%M")

def get_date_str(range_h=None, from_date_str=None, to_date_str=None, callBy='request'):
    if all([x is None for x in [range_h, from_date_str, to_date_str]]):
        range_h = request.args.get('range_h', None) # This will return a string, if field range_h exists in the request
        from_date_str = request.args.get('from', time.strftime("%Y-%m-%d 00:00")) # Get the from date value from the URL
        to_date_str = request.args.get('to', time.strftime("%Y-%m-%d %H:%M"))   # Get the to date value from the URL
    else:
        callBy = 'others'
    if range_h is not None:
        range_h = int(range_h) # ValueError would be raised if range_h is not a number in string format
        to_date_str = time.strftime("%Y-%m-%d %H:%M")
        from_date_str = get_datetime_string_hours_before(range_h)
    else:
        # Validate date before sending it to the DB
        if not validate_date(from_date_str):
            from_date_str = time.strftime("%Y-%m-%d 00:00")
        if not validate_date(to_date_str):
            to_date_str = time.strftime("%Y-%m-%d %H:%M")
    return from_date_str, to_date_str, callBy

def get_logs_between(db_path, from_date_str, to_date_str):
    with sqlite3.connect(db_path) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM log WHERE rDateTime BETWEEN ? AND ?", (from_date_str, to_date_str))
        return(curs.fetchall())

def get_records(range_h=None, from_date_str=None, to_date_str=None):
    from_date_str, to_date_str, callBy = get_date_str(range_h, from_date_str, to_date_str)
    logs = get_logs_between(tempHumidity_db_path, from_date_str, to_date_str)
    if callBy == 'request':
        return logs, from_date_str, to_date_str
    else:
        return logs

def validate_date(d):
    try:
        time.strptime(d, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

def get_status_code(status):
    if status == 'on':
        return 100
    else:
        return 0

def get_transition_time_point(aircon_logs, logs):
    if len(aircon_logs) >= 1:
        return datetime(*[int(x) for x in re.split('-| |:', aircon_logs[0][1])])
    else:
        return datetime(*[int(x) for x in logs[-1][:6]])

def appendAirconStatus(logs):
    from_date_str, to_date_str, callBy = get_date_str()
    aircon_logs = get_logs_between(aircon_db_path, from_date_str, to_date_str)
    with sqlite3.connect(aircon_db_path) as conn:
        curs = conn.cursor()
        curs.execute("SELECT * FROM log WHERE rDateTime < ? ORDER BY id DESC LIMIT 1", (from_date_str,))
        previous_log = curs.fetchall()
    try:
        status = get_status_code(previous_log[0][2])
    # if there is no existing previous log, the 'IndexError: list index out of range' error would be raised.
    except IndexError:
        status = 0
    transition_time_point = get_transition_time_point(aircon_logs, logs)
    for log in logs:
        if datetime(*[int(x) for x in log[:6]]) > transition_time_point:
            status = get_status_code(aircon_logs[0][2])
            del aircon_logs[0]
            transition_time_point = get_transition_time_point(aircon_logs, logs)
        log.append(status)
    return logs

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)