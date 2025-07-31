from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Dictionary to store active connections by match_id
        self.active_connections: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, match_id: int):
        """Accept WebSocket connection and add to match room"""
        await websocket.accept()
        if match_id not in self.active_connections:
            self.active_connections[match_id] = []
        self.active_connections[match_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, match_id: int):
        """Remove WebSocket connection from match room"""
        if match_id in self.active_connections:
            self.active_connections[match_id].remove(websocket)
            if not self.active_connections[match_id]:
                del self.active_connections[match_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket connection"""
        await websocket.send_text(message)
    
    async def broadcast_to_match(self, message: str, match_id: int):
        """Broadcast message to all connections in a match room"""
        if match_id in self.active_connections:
            for connection in self.active_connections[match_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Connection is closed, remove it
                    self.active_connections[match_id].remove(connection)
    
    async def broadcast_global(self, message: str):
        """Broadcast message to all connections"""
        for match_connections in self.active_connections.values():
            for connection in match_connections:
                try:
                    await connection.send_text(message)
                except:
                    pass

manager = ConnectionManager()

# PUBLIC_INTERFACE
async def websocket_endpoint(websocket: WebSocket, match_id: int):
    """
    WebSocket endpoint for real-time emoji reactions and match updates.
    
    Args:
        websocket: WebSocket connection
        match_id: ID of the match to connect to
        
    Handles:
        - Real-time emoji reactions
        - Match status updates
        - Viewer count updates
        - Live analytics updates
    """
    await manager.connect(websocket, match_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "reaction":
                    # Handle new emoji reaction
                    emoji_data = message.get("emoji")
                    user_session = message.get("user_session")
                    
                    # Broadcast reaction to all users in the match
                    reaction_message = {
                        "type": "new_reaction",
                        "match_id": match_id,
                        "emoji": emoji_data,
                        "user_session": user_session,
                        "timestamp": message.get("timestamp")
                    }
                    
                    await manager.broadcast_to_match(
                        json.dumps(reaction_message), 
                        match_id
                    )
                
                elif message_type == "ping":
                    # Handle ping/keepalive
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, match_id)

# PUBLIC_INTERFACE
async def broadcast_match_update(match_id: int, update_data: dict):
    """
    Broadcast match updates to all connected clients.
    
    Args:
        match_id: ID of the match being updated
        update_data: Dictionary containing update information
    """
    message = {
        "type": "match_update",
        "match_id": match_id,
        "data": update_data
    }
    await manager.broadcast_to_match(json.dumps(message), match_id)

# PUBLIC_INTERFACE  
async def broadcast_analytics_update(match_id: int, analytics_data: dict):
    """
    Broadcast analytics updates to connected clients.
    
    Args:
        match_id: ID of the match
        analytics_data: Analytics data to broadcast
    """
    message = {
        "type": "analytics_update", 
        "match_id": match_id,
        "data": analytics_data
    }
    await manager.broadcast_to_match(json.dumps(message), match_id)
