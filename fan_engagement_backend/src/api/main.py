from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import matches, reactions, analytics, websocket
from src.database.connection import init_database
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# PUBLIC_INTERFACE
@app.get("/", tags=["health"])
def health_check():
    """
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
    }
