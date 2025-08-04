#!/usr/bin/env python3
"""
Health check script for Fan Engagement Backend API

This script verifies that all API endpoints are working correctly.
"""

import asyncio
import httpx
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def check_endpoint(client: httpx.AsyncClient, endpoint: str, method: str = "GET", data: dict = None):
    """Check a single endpoint"""
    try:
        if method == "GET":
            response = await client.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = await client.post(f"{BASE_URL}{endpoint}", json=data)
        
        if response.status_code in [200, 201]:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {method} {endpoint} - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {e}")
        return False

async def main():
    """Run health checks on all endpoints"""
    print("🏥 Running Fan Engagement Backend Health Check")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        checks = []
        
        # Health check endpoint
        checks.append(await check_endpoint(client, "/"))
        
        # Matches endpoints
        checks.append(await check_endpoint(client, "/matches/"))
        checks.append(await check_endpoint(client, "/matches/1"))
        checks.append(await check_endpoint(client, "/matches/live/current"))
        checks.append(await check_endpoint(client, "/matches/upcoming/next"))
        
        # Analytics endpoints
        checks.append(await check_endpoint(client, "/analytics/global"))
        checks.append(await check_endpoint(client, "/analytics/match/1"))
        checks.append(await check_endpoint(client, "/analytics/summary"))
        
        # Reactions endpoints
        checks.append(await check_endpoint(client, "/reactions/emojis"))
        checks.append(await check_endpoint(client, "/reactions/match/1/recent"))
        
        # Test emoji reaction submission
        reaction_data = {
            "match_id": 1,
            "emoji_type": "❤️",
            "user_id": "health_check_user"
        }
        checks.append(await check_endpoint(client, "/reactions/emoji_reaction", "POST", reaction_data))
        
        # WebSocket info endpoint
        checks.append(await check_endpoint(client, "/ws/info"))
        
        # API documentation
        checks.append(await check_endpoint(client, "/docs"))
        checks.append(await check_endpoint(client, "/openapi.json"))
    
    print("-" * 50)
    passed = sum(checks)
    total = len(checks)
    print(f"📊 Results: {passed}/{total} endpoints passed")
    
    if passed == total:
        print("🎉 All health checks passed! Backend is ready.")
        return 0
    else:
        print("⚠️  Some health checks failed. Please check the logs.")
        return 1

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n⏹️  Health check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Health check failed with error: {e}")
        sys.exit(1)
