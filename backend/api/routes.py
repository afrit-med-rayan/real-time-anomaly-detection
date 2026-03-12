"""
backend/api/routes.py
---------------------
Defines the REST endpoints and the WebSocket connection manager.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services import anomaly_service

router = APIRouter()

# ─── REST Endpoints ───────────────────────────────────────────────────────

@router.get("/events", response_model=List[Dict[str, Any]])
async def get_events(limit: int = 100):
    """
    Get the most recent transactions processed by the system.
    """
    return anomaly_service.get_recent_events(limit=limit)

@router.get("/anomalies", response_model=List[Dict[str, Any]])
async def get_anomalies(limit: int = 100):
    """
    Get the most recent transactions flagged as anomalies.
    """
    return anomaly_service.get_recent_anomalies(limit=limit)

@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics():
    """
    Get basic operational metrics (total observed, anomaly rate, etc.).
    """
    return anomaly_service.get_metrics()


# ─── WebSocket ────────────────────────────────────────────────────────────

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # We need to broadcast to a copy of the list so we don't hit 
        # RuntimeError if connections are removed during iteration.
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for the frontend to receive real-time streams
    of processed transactions.
    """
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect messages from the client.
            # But we must listen to keep the connection open and detect disconnects.
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
