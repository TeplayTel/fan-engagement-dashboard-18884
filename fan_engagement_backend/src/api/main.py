from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .routes import emojis, matches, reactions, analytics
from .websocket import websocket_endpoint

app = FastAPI(
    title="Fan Engagement Backend API",
    description="Backend API for emoji reactions, match management, and analytics with real-time WebSocket support",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check endpoints"
        },
        {
            "name": "emojis", 
            "description": "Emoji asset management operations"
        },
        {
            "name": "matches",
            "description": "Match management operations"
        },
        {
            "name": "reactions",
            "description": "User emoji reaction operations"
        },
        {
            "name": "analytics",
            "description": "Live analytics and statistics"
        },
        {
            "name": "websocket",
            "description": "Real-time WebSocket connections for live updates"
        }
    ]
)

@app.on_event("startup")
async def startup_event():
    """
    Initialize database tables on application startup.
    This ensures database is available before creating tables.
    """
    try:
        from ..models.database import engine, Base
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not initialize database tables: {e}")
        print("Database tables will be created when first accessed")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(emojis.router)
app.include_router(matches.router)
app.include_router(reactions.router)
app.include_router(analytics.router)

# WebSocket endpoint
@app.websocket("/ws/{match_id}")
async def websocket_match_endpoint(websocket: WebSocket, match_id: int):
    """
    WebSocket endpoint for real-time match updates and emoji reactions.
    
    Connect to this endpoint to receive live updates for a specific match:
    - New emoji reactions from other users
    - Match status changes (score updates, live status)
    - Real-time analytics updates
    - Viewer count changes
    
    Usage: ws://localhost:8000/ws/{match_id}
    """
    await websocket_endpoint(websocket, match_id)

# PUBLIC_INTERFACE
@app.get("/", tags=["health"])
def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        Simple health status message
    """
    return {"message": "Healthy", "status": "ok"}

# PUBLIC_INTERFACE
@app.get("/websocket/info", tags=["websocket"])
def websocket_info():
    """
    Information about WebSocket usage and connection details.
    
    Returns:
        WebSocket connection information and usage examples
    """
    return {
        "websocket_url": "/ws/{match_id}",
        "description": "Connect to receive real-time updates for a specific match",
        "message_types": {
            "outgoing": {
                "reaction": "Send emoji reaction: {type: 'reaction', emoji: {...}, user_session: 'session_id', timestamp: '2024-01-01T00:00:00Z'}",
                "ping": "Keepalive: {type: 'ping'}"
            },
            "incoming": {
                "new_reaction": "New emoji reaction from another user",
                "match_update": "Match status or score update", 
                "analytics_update": "Real-time analytics data",
                "pong": "Response to ping"
            }
        },
        "example_connection": "ws://localhost:8000/ws/1"
    }
