# Raspberry Pi Deployment Guide

## Prerequisites

1. Install Python 3 and pip:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## Installation

1. Create a dedicated user and directory:
```bash
sudo useradd --system --shell /bin/false spacontrol
sudo mkdir -p /opt/spacontrol
sudo chown spacontrol:spacontrol /opt/spacontrol
```

2. Copy the project files to `/opt/spacontrol`:
```bash
sudo cp -r . /opt/spacontrol/
sudo chown -R spacontrol:spacontrol /opt/spacontrol
```

3. Create a virtual environment as the spacontrol user:
```bash
sudo -u spacontrol bash -c "cd /opt/spacontrol && python3 -m venv venv"
sudo -u spacontrol bash -c "cd /opt/spacontrol && venv/bin/pip install -r requirements.txt"
```

4. Update spa IP addresses in `config.py` if needed

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
