# Raspberry Pi Deployment Guide

## Prerequisites

1. Install Python 3 and pip:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## Installation

1. Clone or copy the project to `/home/pi/spacontrol`
2. Create a virtual environment:
```bash
cd /home/pi/spacontrol
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Update spa IP addresses in `config.py` if needed

## SystemD Service Setup

1. Copy the service file to systemd:
```bash
sudo cp spacontrol.service /etc/systemd/system/
```

2. Reload systemd and enable the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable spacontrol.service
```

3. Start the service:
```bash
sudo systemctl start spacontrol.service
```

## Service Management Commands

- **Start service:** `sudo systemctl start spacontrol`
- **Stop service:** `sudo systemctl stop spacontrol`  
- **Restart service:** `sudo systemctl restart spacontrol`
- **Check status:** `sudo systemctl status spacontrol`
- **View logs:** `sudo journalctl -u spacontrol -f`
- **Enable auto-start:** `sudo systemctl enable spacontrol`
- **Disable auto-start:** `sudo systemctl disable spacontrol`

## Accessing the Application

Once running, the spa control interface will be available at:
- http://[raspberry-pi-ip]:8000
- http://localhost:8000 (if accessing from the Pi directly)

## Troubleshooting

- Check service status: `sudo systemctl status spacontrol`
- View recent logs: `sudo journalctl -u spacontrol -n 50`
- Follow live logs: `sudo journalctl -u spacontrol -f`
