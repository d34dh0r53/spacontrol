# Spa Control

A web application to control and monitor dual Balboa Water Group WiFi spa controllers.

## Features

- Monitor temperature, pump status, and lights for two spa controllers
- Set target temperature for each spa
- Control pumps and lights independently
- Real-time status updates via WebSocket
- REST API for all control functions

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your spa IP addresses:
```bash
export SPA1_IP="192.168.1.100"
export SPA2_IP="192.168.1.101"
export SPA1_NAME="Main Spa"
export SPA2_NAME="Hot Tub"
```

3. Run the application:
```bash
python main.py
```

4. Open your browser to http://localhost:8000

## API Endpoints

- `GET /api/status` - Get status of both spas
- `GET /api/spa/{spa_id}/status` - Get status of specific spa
- `POST /api/spa/{spa_id}/temperature` - Set target temperature
- `POST /api/spa/{spa_id}/pump/{pump_id}` - Toggle pump on/off
- `POST /api/spa/{spa_id}/light` - Toggle light on/off

## WebSocket

Connect to `ws://localhost:8000/ws` for real-time status updates.

## Configuration

Edit the IP addresses in `config.py` or use environment variables to match your Balboa WiFi module IP addresses.

## Requirements

- Python 3.8+
- Balboa Water Group WiFi modules (bwa™ Wi-Fi Module 50350)
- Network access to both spa controllers
