import sqlite3
import random
import time
from datetime import datetime

def insert_sensor_data():
    conn = sqlite3.connect('farm.db')
    cursor = conn.cursor()

    temperature = round(random.uniform(20.0, 35.0), 2)
    humidity = round(random.uniform(40.0, 80.0), 2)
    soil_moisture = round(random.uniform(30.0, 60.0), 2)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data 
    (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL,
    soil_moisture REAL
    )
    ''')

    cursor.execute('''
    INSERT INTO sensor_data (timestamp, temperature, humidity, soil_moisture)
    VALUES (?, ?, ?, ?)
    ''', (timestamp, temperature, humidity, soil_moisture))

    conn.commit()
    conn.close()

    print(f"✔ Inserted at {timestamp}: Temp={temperature}, Humidity={humidity}, Soil={soil_moisture}")

# Infinite loop - inserts data every 10 seconds
while True:
    insert_sensor_data()
    time.sleep(10)

