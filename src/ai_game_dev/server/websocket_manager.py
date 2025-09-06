import asyncio
import json
from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.project_subscribers: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from project subscriptions
        for project_id, subscribers in self.project_subscribers.items():
            if websocket in subscribers:
                subscribers.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except:
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def subscribe_to_project(self, websocket: WebSocket, project_id: str):
        if project_id not in self.project_subscribers:
            self.project_subscribers[project_id] = []
        
        if websocket not in self.project_subscribers[project_id]:
            self.project_subscribers[project_id].append(websocket)

    async def send_project_update(self, project_id: str, update: dict):
        if project_id in self.project_subscribers:
            disconnected = []
            for connection in self.project_subscribers[project_id]:
                try:
                    await connection.send_text(json.dumps({
                        "type": "project_update",
                        "project_id": project_id,
                        "timestamp": datetime.now().isoformat(),
                        **update
                    }))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected clients
            for connection in disconnected:
                if connection in self.project_subscribers[project_id]:
                    self.project_subscribers[project_id].remove(connection)

    async def send_generation_progress(self, project_id: str, progress: dict):
        await self.send_project_update(project_id, {
            "type": "generation_progress",
            "progress": progress
        })

    async def send_generation_complete(self, project_id: str, result: dict):
        await self.send_project_update(project_id, {
            "type": "generation_complete",
            "result": result
        })

    async def send_generation_error(self, project_id: str, error: str):
        await self.send_project_update(project_id, {
            "type": "generation_error",
            "error": error
        })

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe_project":
                project_id = message.get("project_id")
                if project_id:
                    await websocket_manager.subscribe_to_project(websocket, project_id)
                    await websocket_manager.send_personal_message({
                        "type": "subscription_confirmed",
                        "project_id": project_id
                    }, websocket)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)