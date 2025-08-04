from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import matches, reactions, analytics, websocket
from src.database.connection import init_database
import logging

<<<<<<< HEAD
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
=======
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
>>>>>>> cga-cg3c87e1d1

# FastAPI app with comprehensive metadata for OpenAPI documentation
app = FastAPI(
    title="Fan Engagement Backend API",
    description="""
    Backend API for the Fan Engagement sports streaming application.
    
    ## Features
    
    * **Match Data**: Get live, upcoming, and completed matches with filtering
    * **Emoji Reactions**: Submit and track user emoji reactions to matches  
    * **Analytics**: Real-time and historical analytics for matches and global engagement
    * **WebSocket**: Real-time updates for reactions and analytics via WebSocket
    
    ## Real-time Updates
    
    Connect to the WebSocket endpoint at `/ws/analytics` to receive real-time updates:
    - New emoji reactions from all users
    - Updated global analytics data
    - Match score and status changes
    
    ## Usage Notes
    
    This API uses mock data for development and testing. All match data, 
    analytics, and reactions are simulated in-memory data that resets on server restart.
    """,
    version="1.0.0",
    contact={
        "name": "Fan Engagement API Support",
        "email": "support@fanengagement.com",
    },
    license_info={
        "name": "MIT License", 
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "matches",
            "description": "Operations with match data - get live matches, upcoming games, and historical results"
        },
        {
            "name": "reactions", 
            "description": "Emoji reaction system - submit reactions and get reaction data"
        },
        {
            "name": "analytics",
            "description": "Analytics and insights - match statistics and global engagement metrics"
        },
        {
            "name": "websocket",
            "description": "Real-time WebSocket connections for live updates and broadcasting"
        }
    ]
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
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
=======
# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Include API routers
app.include_router(matches.router)
app.include_router(reactions.router) 
app.include_router(analytics.router)
app.include_router(websocket.router)
>>>>>>> cga-cg3c87e1d1

# PUBLIC_INTERFACE
@app.get("/", tags=["health"])
def health_check():
    """
<<<<<<< HEAD
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
=======
    Health check endpoint to verify API availability.
    
    Returns:
        Basic health status and API information
    """
    return {
        "message": "Fan Engagement Backend API is healthy",
        "status": "online",
        "version": "1.0.0",
        "features": [
            "Match data with filtering",
            "Emoji reactions system", 
            "Real-time analytics",
            "WebSocket broadcasting"
        ],
        "endpoints": {
            "matches": "/matches",
            "reactions": "/reactions", 
            "analytics": "/analytics",
            "websocket": "/ws/analytics",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
>>>>>>> cga-cg3c87e1d1
    }
