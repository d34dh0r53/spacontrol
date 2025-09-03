from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from typing import Dict, List
from spa_controller import SpaControllerManager
from models import SpaStatus, SpaCommand

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize spa controller manager
spa_manager = SpaControllerManager()

# WebSocket connections for real-time updates
active_connections: List[WebSocket] = []

async def monitor_spas():
    """Background task to monitor spa status and broadcast updates"""
    while True:
        try:
            status = await spa_manager.get_all_status()
            logger.info(f"Status update: {status}")
            
            # Convert SpaStatus objects to dictionaries for JSON serialization
            status_dict = {}
            for spa_id, spa_status in status.items():
                status_dict[spa_id] = spa_status.model_dump()
            
            message = json.dumps(status_dict, default=str)
            logger.info(f"Broadcasting to {len(manager.active_connections)} connections")
            await manager.broadcast(message)
            await asyncio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error monitoring spas: {e}")
            await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    await spa_manager.initialize()
    # Start background task to monitor spa status
    monitor_task = asyncio.create_task(monitor_spas())
    
    yield
    
    # Shutdown
    monitor_task.cancel()
    await spa_manager.disconnect_all()

app = FastAPI(title="Spa Control", description="Dual Balboa Spa Controller", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    logger.info(f"WebSocket connected. Total connections: {len(manager.active_connections)}")
    try:
        while True:
            data = await websocket.receive_text()
            # Handle WebSocket commands if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(manager.active_connections)}")

@app.get("/")
async def get():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Spa Control</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>Dual Spa Controller</h1>
            
            <!-- Lighting Control -->
            <div class="global-controls">
                <div class="section-title">Lighting</div>
                <div class="controls-grid">
                    <button id="global-light" class="control-button light-btn inactive global-light-btn" data-spa-id="2">
                        <span>💡 Spa Lights</span>
                    </button>
                </div>
            </div>
            
            <div class="spas-grid">
                <!-- Spa 1 -->
                <div class="spa-card">
                    <div class="spa-header">
                        <div class="spa-name">Swim Spa</div>
                        <div id="status-1" class="connection-status disconnected">Disconnected</div>
                    </div>
                    
                    <div class="temperature-section">
                        <div class="temp-display">
                            <div class="temp-label">Current Temperature</div>
                            <div id="current-temp-1" class="temp-value">--</div>
                        </div>
                        <div class="temp-display">
                            <div class="temp-label">Target Temperature</div>
                            <div id="target-temp-1" class="temp-value temp-display-container">--</div>
                            <div class="temp-controls">
                                <button class="temp-btn temp-down-btn" data-spa-id="1">❄️</button>
                                <input type="number" id="temp-input-1" class="temp-input" min="80" max="104" step="1" data-spa-id="1" placeholder="Set temp">
                                <button class="temp-btn temp-up-btn" data-spa-id="1">🔥</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="controls-section">
                        <div class="section-title">Pumps</div>
                        <div class="controls-grid">
                            <button id="pump-1-0" class="control-button pump-btn inactive" data-spa-id="1" data-pump-id="0">
                                <span>Pump 1</span>
                                <small>OFF</small>
                            </button>
                            <button id="pump-1-1" class="control-button pump-btn inactive" data-spa-id="1" data-pump-id="1">
                                <span>Pump 2</span>
                                <small>OFF</small>
                            </button>
                        </div>
                    </div>
                    

                    
                    <div id="last-update-1" class="status-info">Last updated: --</div>
                </div>
                
                <!-- Spa 2 -->
                <div class="spa-card">
                    <div class="spa-header">
                        <div class="spa-name">Spa</div>
                        <div id="status-2" class="connection-status disconnected">Disconnected</div>
                    </div>
                    
                    <div class="temperature-section">
                        <div class="temp-display">
                            <div class="temp-label">Current Temperature</div>
                            <div id="current-temp-2" class="temp-value">--</div>
                        </div>
                        <div class="temp-display">
                            <div class="temp-label">Target Temperature</div>
                            <div id="target-temp-2" class="temp-value temp-display-container">--</div>
                            <div class="temp-controls">
                                <button class="temp-btn temp-down-btn" data-spa-id="2">❄️</button>
                                <input type="number" id="temp-input-2" class="temp-input" min="80" max="104" step="1" data-spa-id="2" placeholder="Set temp">
                                <button class="temp-btn temp-up-btn" data-spa-id="2">🔥</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="controls-section">
                        <div class="section-title">Pumps</div>
                        <div class="controls-grid">
                            <button id="pump-2-0" class="control-button pump-btn inactive" data-spa-id="2" data-pump-id="0">
                                <span>Pump 1</span>
                                <small>OFF</small>
                            </button>
                            <button id="pump-2-1" class="control-button pump-btn inactive" data-spa-id="2" data-pump-id="1">
                                <span>Pump 2</span>
                                <small>OFF</small>
                            </button>
                        </div>
                    </div>
                    
                    <div id="last-update-2" class="status-info">Last updated: --</div>
                </div>
            </div>
        </div>
        
        <script src="/static/app.js"></script>
    </body>
    </html>
    """)

@app.get("/api/status")
async def get_status():
    """Get status of both spa controllers"""
    status = await spa_manager.get_all_status()
    # Convert SpaStatus objects to dictionaries for JSON response
    return {spa_id: spa_status.model_dump() for spa_id, spa_status in status.items()}

@app.get("/api/spa/{spa_id}/status")
async def get_spa_status(spa_id: int):
    """Get status of specific spa controller"""
    status = await spa_manager.get_spa_status(spa_id)
    return status.model_dump()

@app.post("/api/spa/{spa_id}/temperature")
async def set_temperature(spa_id: int, request: dict):
    """Set target temperature for specific spa"""
    temperature = request.get("temperature")
    await spa_manager.set_temperature(spa_id, temperature)
    return {"status": "success", "spa_id": spa_id, "temperature": temperature}

@app.post("/api/spa/{spa_id}/pump/{pump_id}")
async def cycle_pump(spa_id: int, pump_id: int):
    """Cycle pump through states (Off -> Low -> High -> Off) for specific spa"""
    await spa_manager.cycle_pump(spa_id, pump_id)
    return {"status": "success", "spa_id": spa_id, "pump_id": pump_id, "action": "cycled"}

@app.post("/api/spa/{spa_id}/light")
async def cycle_light(spa_id: int):
    """Cycle light through available modes for specific spa"""
    await spa_manager.cycle_light(spa_id)
    return {"status": "success", "spa_id": spa_id, "action": "cycled"}

@app.post("/api/spa/{spa_id}/light/toggle")
async def toggle_light(spa_id: int, request: dict):
    """Toggle light on/off for specific spa (deprecated - use cycle instead)"""
    state = request.get("state", False)
    await spa_manager.set_light(spa_id, state)
    return {"status": "success", "spa_id": spa_id, "light": state}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
