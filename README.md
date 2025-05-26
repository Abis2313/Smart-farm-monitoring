# Smart Farm Monitoring System

## Project Overview
Smart Farm Monitoring System is a web application designed to monitor key environmental factors such as temperature, humidity, and soil moisture in a farm. It collects sensor data, displays real-time charts, sends alerts when thresholds are exceeded, and allows farmers to download sensor data for offline analysis. This system helps farmers optimize crop growth by providing timely and actionable data.

## Technologies Used
- Python 3.x
- Flask (Web Framework)
- SQLite (Lightweight Database)
- Chart.js (JavaScript Charting Library)
- HTML, CSS, JavaScript (Frontend)
- Random data generation to simulate sensor inputs (can be replaced by real sensors)

## Setup Instructions

### Prerequisites
- Python 3.x installed
- `pip` package manager

### Installation and Running

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-farm-monitoring.git
cd smart-farm-monitoring

# (Optional) Create and activate virtual environment
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
