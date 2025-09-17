import { setStatusLight } from './utils/dom.js';

class SimulationSocket {
    constructor() {
        this.socket = null;
        this.handlers = new Map();
        this.statusElement = document.getElementById('connection-indicator');
    }

    connect(scenarioId) {
        if (!scenarioId) return;
        this.disconnect();
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const url = `${protocol}://${window.location.host}/ws/simulation/${scenarioId}`;
        this.socket = new WebSocket(url);
        this.socket.addEventListener('open', () => {
            setStatusLight(this.statusElement, 'online');
        });
        this.socket.addEventListener('close', () => {
            setStatusLight(this.statusElement, 'offline');
        });
        this.socket.addEventListener('message', (event) => {
            try {
                const data = JSON.parse(event.data);
                this.dispatch(data.type, data);
            } catch (error) {
                console.error('Failed to parse WebSocket message', error);
            }
        });
    }

    disconnect() {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    on(eventType, callback) {
        this.handlers.set(eventType, callback);
    }

    dispatch(eventType, payload) {
        const handler = this.handlers.get(eventType);
        if (handler) {
            handler(payload);
        }
    }
}

export const simulationSocket = new SimulationSocket();
