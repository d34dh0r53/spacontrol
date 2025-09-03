from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class SpaStatus(BaseModel):
    spa_id: int
    connected: bool
    current_temp: Optional[float] = None
    target_temp: Optional[float] = None
    heat_mode: Optional[str] = None
    pumps: Dict[int, int] = {}  # 0=Off, 1=Low, 2=High, etc.
    lights: bool = False
    light_mode: Optional[str] = None
    filter_mode: Optional[str] = None
    circulation_pump: bool = False
    mac_address: Optional[str] = None
    last_update: datetime
    
class SpaCommand(BaseModel):
    spa_id: int
    command: str
    parameters: Dict[str, Any] = {}

class SpaConfig(BaseModel):
    spa_id: int
    name: str
    ip_address: str
    port: int = 4257
    enabled: bool = True
