from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from src.services.websocket_manager import connection_manager
from src.services.mock_data import mock_data_service

router = APIRouter(tags=["websocket"])

# PUBLIC_INTERFACE
@router.websocket("/ws/analytics")
async def websocket_analytics_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time analytics updates.
    
    This WebSocket connection provides real-time updates for:
    - New emoji reactions from users
    - Updated global analytics data
    - Match status changes
    - Live reaction counts and distributions
    
    Usage:
        Connect to this endpoint to receive real-time analytics data.
        The server will automatically broadcast updates when:
        1. New emoji reactions are submitted
        2. Match data changes (score updates, status changes)
        3. Analytics are recalculated
    
    Message Format:
        {
            "type": "reaction" | "analytics_update" | "match_update",
            "data": {...},
            "timestamp": "2024-01-01T12:00:00Z"
        }
    
    Connection Management:
        - Clients are automatically added to the broadcast list on connect
        - Failed connections are automatically cleaned up
        - Connection count is tracked for analytics
    """
    await connection_manager.connect(websocket)
    
    try:
        # Send initial analytics data to the newly connected client
        initial_analytics = mock_data_service.get_global_analytics()
        await connection_manager.send_personal_message(
            json.dumps({
                "type": "initial_analytics",
                "data": initial_analytics.model_dump(),
                "timestamp": initial_analytics.__dict__.get("timestamp", "")
            }),
            websocket
        )
        
        # Keep the connection alive and handle incoming messages
        while True:
            # Wait for any message from client (could be heartbeat, preferences, etc.)
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types from client
                if message.get("type") == "heartbeat":
                    await connection_manager.send_personal_message(
                        json.dumps({"type": "heartbeat_ack", "timestamp": message.get("timestamp")}),
                        websocket
                    )
                elif message.get("type") == "request_analytics":
                    # Client requesting fresh analytics data
                    current_analytics = mock_data_service.get_global_analytics()
                    await connection_manager.send_personal_message(
                        json.dumps({
                            "type": "analytics_update",
                            "data": current_analytics.model_dump(),
                            "timestamp": current_analytics.__dict__.get("timestamp", "")
                        }),
                        websocket
                    )
                
            except json.JSONDecodeError:
                # Invalid JSON received, send error message
                await connection_manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}),
                    websocket
                )
            except Exception as e:
                print(f"Error processing client message: {e}")
                
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        print("Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")
        connection_manager.disconnect(websocket)

# PUBLIC_INTERFACE  
@router.get("/ws/info")
async def websocket_info():
    """
    Get information about WebSocket connections and usage.
    
    Returns:
        Information about active WebSocket connections and usage instructions
    """
    return {
        "endpoint": "/ws/analytics",
        "active_connections": connection_manager.get_connection_count(),
        "description": "WebSocket endpoint for real-time analytics updates",
        "message_types": [
            {
                "type": "reaction",
                "description": "New emoji reaction submitted",
                "example_data": {
                    "match_id": 1,
                    "emoji": "❤️",
                    "user_id": "user123",
                    "timestamp": "2024-01-01T12:00:00Z",
                    "match_name": "Arsenal vs Chelsea"
                }
            },
            {
                "type": "analytics_update", 
                "description": "Global analytics data updated",
                "example_data": {
                    "total_reactions": 1250,
                    "total_users": 2300,
                    "active_matches": 3,
                    "emoji_distribution": {"❤️": 450, "🔥": 320}
                }
            },
            {
                "type": "match_update",
                "description": "Match information updated (score, status, etc.)",
                "example_data": {
                    "match_id": 1,
                    "score": {"home": 3, "away": 1},
                    "match_time": "82'",
                    "status": "live"
                }
            }
        ],
        "client_messages": [
            {
                "type": "heartbeat",
                "description": "Keep connection alive",
                "example": {"type": "heartbeat", "timestamp": "2024-01-01T12:00:00Z"}
            },
            {
                "type": "request_analytics",
                "description": "Request fresh analytics data",
                "example": {"type": "request_analytics"}
            }
        ]
    }
