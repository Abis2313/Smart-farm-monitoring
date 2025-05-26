import random
import csv
from flask import make_response, redirect, url_for, session
from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  

ALERT_THRESHOLDS = {
    'temperature': {'min': 15, 'max': 30},  
    'humidity': {'min': 30, 'max': 70},     
    'soil_moisture': {'min': 25, 'max': 55} 
}

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'farm123':
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid Credentials. Try again.'

    return render_template('login.html', error=error)


def check_alerts():
    conn = sqlite3.connect('farm.db')
    cursor = conn.cursor()
    cursor.execute('SELECT temperature, humidity, soil_moisture FROM sensor_data ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()

    if not row:
        return [] 

    temperature, humidity, soil_moisture = row
    alerts = []

    if temperature < ALERT_THRESHOLDS['temperature']['min']:
        alerts.append(f"Temperature too LOW: {temperature}°C (below {ALERT_THRESHOLDS['temperature']['min']}°C)")
    elif temperature > ALERT_THRESHOLDS['temperature']['max']:
        alerts.append(f"Temperature too HIGH: {temperature}°C (above {ALERT_THRESHOLDS['temperature']['max']}°C)")

    if humidity < ALERT_THRESHOLDS['humidity']['min']:
        alerts.append(f"Humidity too LOW: {humidity}% (below {ALERT_THRESHOLDS['humidity']['min']}%)")
    elif humidity > ALERT_THRESHOLDS['humidity']['max']:
        alerts.append(f"Humidity too HIGH: {humidity}% (above {ALERT_THRESHOLDS['humidity']['max']}%)")

    if soil_moisture < ALERT_THRESHOLDS['soil_moisture']['min']:
        alerts.append(f"Soil moisture too LOW: {soil_moisture}% (below {ALERT_THRESHOLDS['soil_moisture']['min']}%)")
    elif soil_moisture > ALERT_THRESHOLDS['soil_moisture']['max']:
        alerts.append(f"Soil moisture too HIGH: {soil_moisture}% (above {ALERT_THRESHOLDS['soil_moisture']['max']}%)")

    return alerts


def generate_fake_sensor_data():
    temperature = random.uniform(15, 35)  
    humidity = random.uniform(30, 70)       
    soil_moisture = random.uniform(25, 55) # random float between 25 and 55
    return temperature, humidity, soil_moisture

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        temperature, humidity, soil_moisture = generate_fake_sensor_data()
        alerts = []

        if temperature < ALERT_THRESHOLDS['temperature']['min']:
            alerts.append(f"Temperature too LOW: {temperature:.1f}°C")
        elif temperature > ALERT_THRESHOLDS['temperature']['max']:
            alerts.append(f"Temperature too HIGH: {temperature:.1f}°C")

        if humidity < ALERT_THRESHOLDS['humidity']['min']:
            alerts.append(f"Humidity too LOW: {humidity:.1f}%")
        elif humidity > ALERT_THRESHOLDS['humidity']['max']:
            alerts.append(f"Humidity too HIGH: {humidity:.1f}%")

        if soil_moisture < ALERT_THRESHOLDS['soil_moisture']['min']:
            alerts.append(f"Soil moisture too LOW: {soil_moisture:.1f}%")
        elif soil_moisture > ALERT_THRESHOLDS['soil_moisture']['max']:
            alerts.append(f"Soil moisture too HIGH: {soil_moisture:.1f}%")

        return render_template('dashboard.html', alerts=alerts,
                               temperature=temperature,
                               humidity=humidity,
                               soil_moisture=soil_moisture)
    else:
        return redirect(url_for('login'))
    

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/api/data')
def api_data():
    simulated_temp = round(random.uniform(10, 40), 1)         
    simulated_hum = round(random.uniform(20, 80), 1)       
    simulated_soil = round(random.uniform(10, 60), 1)          

    conn = sqlite3.connect('farm.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (timestamp, temperature, humidity, soil_moisture)
        VALUES (datetime('now'), ?, ?, ?)
    ''', (simulated_temp, simulated_hum, simulated_soil))
    conn.commit()
 
    cursor.execute('SELECT * FROM sensor_data ORDER BY id DESC LIMIT 10')
    data = cursor.fetchall()
 
    alert_message = "Temperature, Humidity, and Soil Moisture are OK."

    if simulated_temp < ALERT_THRESHOLDS['temperature']['min']:
        alert_message = f"Temperature too LOW: {simulated_temp}°C!"
    elif simulated_temp > ALERT_THRESHOLDS['temperature']['max']:
        alert_message = f"Temperature too HIGH: {simulated_temp}°C!"
    elif simulated_hum < ALERT_THRESHOLDS['humidity']['min']:
        alert_message = f"Humidity too LOW: {simulated_hum}%!"
    elif simulated_hum > ALERT_THRESHOLDS['humidity']['max']:
        alert_message = f"Humidity too HIGH: {simulated_hum}%!"
    elif simulated_soil < ALERT_THRESHOLDS['soil_moisture']['min']:
        alert_message = f"Soil moisture too LOW: {simulated_soil}%!"
    elif simulated_soil > ALERT_THRESHOLDS['soil_moisture']['max']:
        alert_message = f"Soil moisture too HIGH: {simulated_soil}%!"

    conn.close()
    return jsonify({'data': data, 'alert': alert_message})



@app.route('/api/post_data', methods=['POST'])
def receive_sensor_data():
    data = request.get_json()

    if not data:
        return jsonify({'status': 'error', 'message': 'No JSON data received'}), 400

    try:
        temp = float(data['temperature'])
        hum = float(data['humidity'])
        soil = float(data['soil_moisture'])
    except (KeyError, ValueError):
        return jsonify({'status': 'error', 'message': 'Invalid or missing sensor data'}), 400

    conn = sqlite3.connect('farm.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (timestamp, temperature, humidity, soil_moisture)
        VALUES (datetime('now'), ?, ?, ?)
    ''', (temp, hum, soil))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success', 'message': 'Sensor data saved'}), 200


@app.route('/export')
def export_csv():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('farm.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sensor_data")
    rows = cursor.fetchall()
    conn.close()

    def generate():
        data = []

        yield 'ID,Timestamp,Temperature (°C),Humidity (%),Soil Moisture (%)\n'
        for row in rows:
            yield ','.join(str(item) for item in row) + '\n'

    return Response(
        generate(),
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=sensor_data.csv"}
    )

if __name__ == '__main__':
    app.run(debug=True)
