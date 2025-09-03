import asyncio
from typing import Dict, List, Optional
from pybalboa import SpaClient
from models import SpaStatus, SpaConfig
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SpaController:
    def __init__(self, config: SpaConfig):
        self.config = config
        self.client: Optional[SpaClient] = None
        self.connected = False
        self.last_status = None
        
    async def connect(self):
        """Connect to the Balboa spa controller"""
        try:
            self.client = SpaClient(self.config.ip_address, self.config.port)
            await self.client.connect()
            
            # Wait for configuration to load
            logger.info(f"Connected to spa {self.config.spa_id} at {self.config.ip_address}, waiting for configuration...")
            await self.client.async_configuration_loaded()
            
            self.connected = True
            logger.info(f"Spa {self.config.spa_id} configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to connect to spa {self.config.spa_id}: {e}")
            self.connected = False
            raise
    
    async def disconnect(self):
        """Disconnect from the spa controller"""
        if self.client:
            try:
                await self.client.disconnect()
            except:
                pass
            finally:
                self.connected = False
                self.client = None
    
    async def get_status(self) -> SpaStatus:
        """Get current status of the spa"""
        if not self.connected or not self.client:
            logger.warning(f"Spa {self.config.spa_id} at {self.config.ip_address} not connected or no client - connected: {self.connected}, client: {self.client is not None}")
            return SpaStatus(
                spa_id=self.config.spa_id,
                connected=False,
                last_update=datetime.now()
            )
        
        try:
            # Check if configuration is loaded
            if not getattr(self.client, 'configuration_loaded', False):
                logger.debug(f"Spa {self.config.spa_id} configuration not yet loaded")
                return SpaStatus(
                    spa_id=self.config.spa_id,
                    connected=True,
                    current_temp=None,
                    target_temp=None,
                    mac_address=getattr(self.client, 'mac_address', None),
                    last_update=datetime.now()
                )
            
            # Parse pump states
            pumps = {}
            if hasattr(self.client, 'pumps') and self.client.pumps:
                for i, pump in enumerate(self.client.pumps):
                    if pump is not None:
                        # Store actual pump state (0=Off, 1=Low, 2=High, etc.)
                        pumps[i] = pump.state
            
            # Parse light states
            lights_on = False
            light_mode = "OFF"
            if hasattr(self.client, 'lights') and self.client.lights:
                logger.info(f"Spa {self.config.spa_id} found {len(self.client.lights)} light(s)")
                for i, light in enumerate(self.client.lights):
                    if light:
                        logger.info(f"Light {i}: state={light.state}, options={light.options if hasattr(light, 'options') else 'None'}, type={type(light)}")
                        if hasattr(light, '__dict__'):
                            logger.info(f"Light {i} attributes: {vars(light)}")
                        if light.state > 0:
                            lights_on = True
                            # Get light mode information
                            if hasattr(light, 'options') and light.options:
                                if light.state < len(light.options):
                                    light_mode = str(light.options[light.state])
                                else:
                                    light_mode = f"MODE_{light.state}"
                            else:
                                light_mode = f"STATE_{light.state}"
                        # Only break after first light for now
                        break
            
            # Safely get temperature values
            current_temp = getattr(self.client, 'temperature', None)
            target_temp = getattr(self.client, 'target_temperature', None)
            heat_mode = getattr(self.client, 'heat_mode', None)
            
            # Circulation pump state
            circ_pump = False
            if hasattr(self.client, 'circulation_pump') and self.client.circulation_pump:
                circ_pump = self.client.circulation_pump.state > 0
            
            status = SpaStatus(
                spa_id=self.config.spa_id,
                connected=True,
                current_temp=current_temp,
                target_temp=target_temp,
                heat_mode=str(heat_mode) if heat_mode else None,
                pumps=pumps,
                lights=lights_on,
                light_mode=light_mode,
                filter_mode=f"Cycle1: {getattr(self.client, 'filter_cycle_1_running', False)}, Cycle2: {getattr(self.client, 'filter_cycle_2_running', False)}",
                circulation_pump=circ_pump,
                mac_address=getattr(self.client, 'mac_address', None),
                last_update=datetime.now()
            )
            
            self.last_status = status
            return status
            
        except Exception as e:
            logger.error(f"Error getting status for spa {self.config.spa_id}: {e}")
            return SpaStatus(
                spa_id=self.config.spa_id,
                connected=False,
                last_update=datetime.now()
            )
    
    async def set_temperature(self, temperature: float):
        """Set target temperature"""
        if not self.connected or not self.client:
            raise Exception(f"Spa {self.config.spa_id} not connected")
        
        try:
            await self.client.set_temperature(temperature)
            logger.info(f"Set temperature for spa {self.config.spa_id} to {temperature}")
        except Exception as e:
            logger.error(f"Error setting temperature for spa {self.config.spa_id}: {e}")
            raise
    
    async def cycle_pump(self, pump_id: int):
        """Cycle pump through states: Off -> Low -> High -> Off"""
        if not self.connected or not self.client:
            raise Exception(f"Spa {self.config.spa_id} not connected")
        
        try:
            if self.client.pumps and len(self.client.pumps) > pump_id:
                pump = self.client.pumps[pump_id]
                if pump:
                    current_state = pump.state
                    logger.info(f"Pump {pump_id} current state: {current_state}, options: {pump.options}")
                    
                    # For most pumps: 0=Off, 1=Low, 2=High
                    # Simple cycle: 0 -> 1 -> 2 -> 0
                    if current_state == 0:
                        next_state = 1  # Off -> Low
                    elif current_state == 1:
                        next_state = 2  # Low -> High  
                    elif current_state == 2:
                        next_state = 0  # High -> Off
                    else:
                        next_state = 0  # Unknown -> Off
                    
                    logger.info(f"Cycling pump {pump_id} for spa {self.config.spa_id} from state {current_state} to {next_state}")
                    await pump.set_state(next_state)
                    
                    state_names = ["OFF", "LOW", "HIGH", "EXTRA"]
                    state_name = state_names[next_state] if next_state < len(state_names) else f"STATE{next_state}"
                    logger.info(f"Successfully cycled pump {pump_id} for spa {self.config.spa_id} to {state_name} (state {next_state})")
        except Exception as e:
            logger.error(f"Error cycling pump for spa {self.config.spa_id}: {e}")
            raise
    
    async def cycle_light(self):
        """Cycle light through available modes"""
        if not self.connected or not self.client:
            raise Exception(f"Spa {self.config.spa_id} not connected")
        
        try:
            if self.client.lights and len(self.client.lights) > 0:
                light = self.client.lights[0]
                if light:
                    current_state = light.state
                    logger.info(f"Light current state: {current_state}, options: {light.options if hasattr(light, 'options') else 'None'}")
                    
                    # Cycle through light modes - use detected options since experimental cycling fails
                    if hasattr(light, 'options') and light.options:
                        max_states = len(light.options)
                        next_state = (current_state + 1) % max_states
                        logger.info(f"Using options-based cycling: {current_state} -> {next_state} (max: {max_states})")
                    else:
                        # Simple fallback: toggle between 0 and 1
                        next_state = 1 if current_state == 0 else 0
                        logger.info(f"Using simple toggle: {current_state} -> {next_state}")
                    
                    logger.info(f"Cycling light for spa {self.config.spa_id} from state {current_state} to {next_state}")
                    await light.set_state(next_state)
                    logger.info(f"Successfully cycled light for spa {self.config.spa_id} to state {next_state}")
            else:
                logger.warning(f"No lights available for spa {self.config.spa_id}")
        except Exception as e:
            logger.error(f"Error cycling light for spa {self.config.spa_id}: {e}")
            raise

    async def set_light(self, state: bool):
        """Set light state (deprecated - use cycle_light instead)"""
        if not self.connected or not self.client:
            raise Exception(f"Spa {self.config.spa_id} not connected")
        
        try:
            if self.client.lights and len(self.client.lights) > 0:
                light = self.client.lights[0]
                if light:
                    # Use the correct pybalboa method to set light state
                    if state:
                        # Set to on (state 1)
                        await light.set_state(1)
                    else:
                        # Set to off (state 0)
                        await light.set_state(0)
            logger.info(f"Set light for spa {self.config.spa_id} to {state}")
        except Exception as e:
            logger.error(f"Error setting light for spa {self.config.spa_id}: {e}")
            raise

class SpaControllerManager:
    def __init__(self):
        self.controllers: Dict[int, SpaController] = {}
        self.configs: List[SpaConfig] = []
        
    async def initialize(self):
        """Initialize spa controllers from config"""
        from config import load_spa_configs
        self.configs = load_spa_configs()
        
        logger.info(f"Loading {len(self.configs)} spa configurations...")
        for config in self.configs:
            logger.info(f"Config: Spa {config.spa_id} - {config.name} at {config.ip_address}:{config.port}, enabled: {config.enabled}")
            
            if config.enabled:
                controller = SpaController(config)
                try:
                    logger.info(f"Attempting to connect to spa {config.spa_id}...")
                    await controller.connect()
                    self.controllers[config.spa_id] = controller
                    logger.info(f"Successfully initialized spa controller {config.spa_id}")
                except Exception as e:
                    logger.error(f"Failed to initialize spa {config.spa_id}: {e}")
            else:
                logger.info(f"Spa {config.spa_id} is disabled, skipping connection")
    
    async def disconnect_all(self):
        """Disconnect all spa controllers"""
        for controller in self.controllers.values():
            await controller.disconnect()
        self.controllers.clear()
    
    async def get_all_status(self) -> Dict[int, SpaStatus]:
        """Get status of all connected spas"""
        status = {}
        logger.debug(f"Getting status for {len(self.controllers)} controllers: {list(self.controllers.keys())}")
        for spa_id, controller in self.controllers.items():
            logger.debug(f"Getting status for spa {spa_id} - connected: {controller.connected}")
            spa_status = await controller.get_status()
            status[spa_id] = spa_status
            logger.debug(f"Spa {spa_id} status: connected={spa_status.connected}, temp={spa_status.current_temp}")
        return status
    
    async def get_spa_status(self, spa_id: int) -> SpaStatus:
        """Get status of specific spa"""
        if spa_id not in self.controllers:
            raise Exception(f"Spa {spa_id} not found")
        return await self.controllers[spa_id].get_status()
    
    async def set_temperature(self, spa_id: int, temperature: float):
        """Set temperature for specific spa"""
        if spa_id not in self.controllers:
            raise Exception(f"Spa {spa_id} not found")
        await self.controllers[spa_id].set_temperature(temperature)
    
    async def cycle_pump(self, spa_id: int, pump_id: int):
        """Cycle pump state for specific spa"""
        if spa_id not in self.controllers:
            raise Exception(f"Spa {spa_id} not found")
        await self.controllers[spa_id].cycle_pump(pump_id)
    
    async def cycle_light(self, spa_id: int):
        """Cycle light state for specific spa"""
        if spa_id not in self.controllers:
            raise Exception(f"Spa {spa_id} not found")
        await self.controllers[spa_id].cycle_light()
    
    async def set_light(self, spa_id: int, state: bool):
        """Set light state for specific spa (deprecated - use cycle_light instead)"""
        if spa_id not in self.controllers:
            raise Exception(f"Spa {spa_id} not found")
        await self.controllers[spa_id].set_light(state)
