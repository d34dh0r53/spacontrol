import os
from typing import List
from models import SpaConfig

def load_spa_configs() -> List[SpaConfig]:
    """Load spa configurations from environment variables or config file"""
    configs = []
    
    # Try to load from environment variables first
    spa1_ip = os.getenv("SPA1_IP")
    spa2_ip = os.getenv("SPA2_IP")
    
    if spa1_ip:
        configs.append(SpaConfig(
            spa_id=1,
            name=os.getenv("SPA1_NAME", "Main Spa"),
            ip_address=spa1_ip,
            port=int(os.getenv("SPA1_PORT", "4257")),
            enabled=True
        ))
    
    if spa2_ip:
        configs.append(SpaConfig(
            spa_id=2,
            name=os.getenv("SPA2_NAME", "Secondary Spa"),
            ip_address=spa2_ip,
            port=int(os.getenv("SPA2_PORT", "4257")),
            enabled=True
        ))
    
    # If no environment variables, use default configs
    if not configs:
        configs = [
            SpaConfig(
                spa_id=1, 
                name="Main Spa", 
                ip_address="172.16.10.140",  # Your working spa IP
                enabled=True  # Enable the working spa
            ),
            SpaConfig(
                spa_id=2, 
                name="Secondary Spa", 
                ip_address="172.16.10.163",  # Your second spa IP
                enabled=True  # Enable the second spa
            )
        ]
    
    return configs
