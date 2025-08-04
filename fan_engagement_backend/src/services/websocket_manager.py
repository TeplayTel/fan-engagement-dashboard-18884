from fastapi import WebSocket
from typing import List, Dict, Any
from datetime import datetime
from src.models.schemas import WebSocketMessage

class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"Client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_analytics_update(self, analytics_data: Dict[str, Any]):
        """Broadcast analytics update to all clients"""
        message = WebSocketMessage(
            type="analytics_update",
            data=analytics_data,
            timestamp=datetime.now()
        )
        await self.broadcast(message.model_dump_json())
    
    async def broadcast_reaction(self, reaction_data: Dict[str, Any]):
        """Broadcast new emoji reaction to all clients"""
        message = WebSocketMessage(
            type="reaction",
            data=reaction_data,
            timestamp=datetime.now()
        )
        await self.broadcast(message.model_dump_json())
    
    async def broadcast_match_update(self, match_data: Dict[str, Any]):
        """Broadcast match update to all clients"""
        message = WebSocketMessage(
            type="match_update",
            data=match_data,
            timestamp=datetime.now()
        )
        await self.broadcast(message.model_dump_json())
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)

# Global connection manager instance
connection_manager = ConnectionManager()
