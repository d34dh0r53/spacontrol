class SpaController {
    constructor() {
        this.ws = null;
        this.reconnectInterval = 5000;
        this.spaData = {};
        this.editingInputs = new Set(); // Track inputs being edited
        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.ws.onmessage = (event) => {
            try {
                this.spaData = JSON.parse(event.data);
                console.log('Received spa data:', this.spaData);
                this.updateUI();
            } catch (error) {
                console.error('Error parsing WebSocket data:', error);
            }
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected, attempting to reconnect...');
            setTimeout(() => this.connectWebSocket(), this.reconnectInterval);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    setupEventListeners() {
        // Temperature controls
        document.addEventListener('click', (e) => {
            // Temperature up button
            if (e.target.matches('.temp-up-btn')) {
                const spaId = e.target.dataset.spaId;
                const input = document.querySelector(`#temp-input-${spaId}`);
                const currentTemp = parseFloat(input.value) || 80;
                const newTemp = Math.min(104, currentTemp + 1);
                input.value = newTemp;
                this.setTemperature(spaId, newTemp);
            }
            
            // Temperature down button
            if (e.target.matches('.temp-down-btn')) {
                const spaId = e.target.dataset.spaId;
                const input = document.querySelector(`#temp-input-${spaId}`);
                const currentTemp = parseFloat(input.value) || 104;
                const newTemp = Math.max(80, currentTemp - 1);
                input.value = newTemp;
                this.setTemperature(spaId, newTemp);
            }
            
            // Pump controls
            if (e.target.matches('.pump-btn')) {
                const spaId = e.target.dataset.spaId;
                const pumpId = e.target.dataset.pumpId;
                this.cyclePump(spaId, pumpId);
            }
            
            // Global light controls (only spa 2 has functional lighting)
            if (e.target.matches('.light-btn')) {
                const spaId = e.target.dataset.spaId;
                this.cycleLight(spaId);
            }
        });

        // Temperature input events
        document.addEventListener('focus', (e) => {
            if (e.target.matches('.temp-input')) {
                const spaId = e.target.dataset.spaId;
                const inputId = `temp-input-${spaId}`;
                this.editingInputs.add(inputId);
                
                // Add visual indicator
                const targetTempElement = document.querySelector(`#target-temp-${spaId}`);
                if (targetTempElement) {
                    targetTempElement.classList.add('temp-editing');
                }
            }
        }, true);

        document.addEventListener('blur', (e) => {
            if (e.target.matches('.temp-input')) {
                const spaId = e.target.dataset.spaId;
                const inputId = `temp-input-${spaId}`;
                const temperature = parseFloat(e.target.value);
                
                // Remove from editing set
                this.editingInputs.delete(inputId);
                
                // Remove visual indicator
                const targetTempElement = document.querySelector(`#target-temp-${spaId}`);
                if (targetTempElement) {
                    targetTempElement.classList.remove('temp-editing');
                }
                
                // Validate and set temperature
                if (temperature >= 80 && temperature <= 104) {
                    this.setTemperature(spaId, temperature);
                } else {
                    alert('Temperature must be between 80°F and 104°F');
                    // Reset to current target temperature
                    const spa = this.spaData[spaId];
                    if (spa && spa.target_temp) {
                        e.target.value = spa.target_temp;
                    }
                }
            }
        }, true);

        // Enter key for temperature input
        document.addEventListener('keypress', (e) => {
            if (e.target.matches('.temp-input') && e.key === 'Enter') {
                e.target.blur(); // Trigger the blur event
            }
        });
    }

    async setTemperature(spaId, temperature) {
        try {
            const response = await fetch(`/api/spa/${spaId}/temperature`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ temperature })
            });
            
            if (!response.ok) {
                throw new Error('Failed to set temperature');
            }
            
            console.log(`Set temperature for spa ${spaId} to ${temperature}°F`);
        } catch (error) {
            console.error('Error setting temperature:', error);
            alert('Failed to set temperature');
        }
    }

    async cyclePump(spaId, pumpId) {
        try {
            const response = await fetch(`/api/spa/${spaId}/pump/${pumpId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to cycle pump');
            }
            
            console.log(`Cycled pump ${pumpId} for spa ${spaId}`);
        } catch (error) {
            console.error('Error cycling pump:', error);
            alert('Failed to cycle pump');
        }
    }

    async cycleLight(spaId) {
        try {
            const response = await fetch(`/api/spa/${spaId}/light`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to cycle light');
            }
            
            console.log(`Cycled light for spa ${spaId}`);
        } catch (error) {
            console.error('Error cycling light:', error);
            alert('Failed to cycle light');
        }
    }

    updateUI() {
        console.log('Updating UI with data:', this.spaData);
        Object.keys(this.spaData).forEach(spaId => {
            const spa = this.spaData[spaId];
            console.log(`Updating spa ${spaId}:`, spa);
            this.updateSpaCard(spaId, spa);
        });
    }

    updateSpaCard(spaId, spa) {
        // Update connection status
        const statusElement = document.querySelector(`#status-${spaId}`);
        if (statusElement) {
            statusElement.textContent = spa.connected ? 'Connected' : 'Disconnected';
            statusElement.className = `connection-status ${spa.connected ? 'connected' : 'disconnected'}`;
        }

        // Update temperatures
        const currentTempElement = document.querySelector(`#current-temp-${spaId}`);
        if (currentTempElement) {
            currentTempElement.textContent = spa.current_temp ? `${spa.current_temp}°F` : '--';
        }

        const targetTempElement = document.querySelector(`#target-temp-${spaId}`);
        if (targetTempElement) {
            targetTempElement.textContent = spa.target_temp ? `${spa.target_temp}°F` : '--';
        }

        // Update temperature input (only if not currently being edited)
        const tempInput = document.querySelector(`#temp-input-${spaId}`);
        const inputId = `temp-input-${spaId}`;
        if (tempInput && spa.target_temp && !this.editingInputs.has(inputId)) {
            tempInput.value = spa.target_temp;
        }

        // Update pumps
        console.log(`Spa ${spaId} pumps:`, spa.pumps);
        Object.keys(spa.pumps || {}).forEach(pumpId => {
            const pumpBtn = document.querySelector(`#pump-${spaId}-${pumpId}`);
            console.log(`Looking for pump button #pump-${spaId}-${pumpId}:`, pumpBtn);
            if (pumpBtn) {
                const pumpState = parseInt(spa.pumps[pumpId]) || 0;
                console.log(`Pump ${pumpId} state:`, pumpState, typeof pumpState);
                
                // Determine CSS class and text based on state
                let className = 'control-button pump-btn';
                let stateText = 'OFF';
                
                if (pumpState === 0) {
                    className += ' inactive';
                    stateText = 'OFF';
                } else if (pumpState === 1) {
                    className += ' active';
                    stateText = 'LOW';
                } else if (pumpState === 2) {
                    className += ' active';
                    stateText = 'HIGH';
                } else if (pumpState > 2) {
                    className += ' active';
                    stateText = `STATE${pumpState}`;
                }
                
                pumpBtn.className = className;
                
                // Update the text inside the button
                const smallElement = pumpBtn.querySelector('small');
                if (smallElement) {
                    smallElement.textContent = stateText;
                }
            } else {
                console.log(`Pump button #pump-${spaId}-${pumpId} not found`);
            }
        });

        // Update global lights (only for spa 2)
        if (spaId === '2') {
            const globalLightBtn = document.querySelector('#global-light');
            if (globalLightBtn) {
                globalLightBtn.className = `control-button light-btn global-light-btn ${spa.lights ? 'active' : 'inactive'}`;
            }
        }

        // Update last update time
        const lastUpdateElement = document.querySelector(`#last-update-${spaId}`);
        if (lastUpdateElement && spa.last_update) {
            const updateTime = new Date(spa.last_update).toLocaleTimeString();
            lastUpdateElement.textContent = `Last updated: ${updateTime}`;
        }
    }
}

// Initialize the spa controller when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SpaController();
});
