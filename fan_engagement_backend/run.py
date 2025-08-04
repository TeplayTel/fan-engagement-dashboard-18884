#!/usr/bin/env python3
"""
Fan Engagement Backend Server Startup Script

This script starts the FastAPI server with proper configuration for development.
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Start the FastAPI server"""
    # Server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print("🚀 Starting Fan Engagement Backend API...")
    print(f"📍 Server will run on: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔌 WebSocket Endpoint: ws://{host}:{port}/ws/analytics")
    print(f"📊 OpenAPI Spec: http://{host}:{port}/openapi.json")
    print(f"🔄 Auto-reload: {'Enabled' if reload else 'Disabled'}")
    print("-" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True,
            reload_dirs=["src"] if reload else None
        )
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
