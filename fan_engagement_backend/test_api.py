#!/usr/bin/env python3
"""
Simple API test script for Fan Engagement Backend

This script performs basic tests on the API endpoints to ensure they work correctly.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.services.mock_data import mock_data_service
from src.models.schemas import EmojiReaction, EmojiType

async def test_mock_data_service():
    """Test the mock data service functionality"""
    print("🧪 Testing Mock Data Service...")
    
    # Test getting matches
    matches = mock_data_service.get_matches()
    print(f"✅ Found {len(matches)} matches")
    
    # Test getting specific match
    match = mock_data_service.get_match_by_id(1)
    if match:
        print(f"✅ Retrieved match: {match.home_team.name} vs {match.away_team.name}")
    else:
        print("❌ Failed to retrieve match by ID")
        return False
    
    # Test filtering matches
    live_matches = mock_data_service.get_matches({"status": "live"})
    print(f"✅ Found {len(live_matches)} live matches")
    
    # Test adding emoji reaction
    reaction = EmojiReaction(
        match_id=1,
        emoji_type=EmojiType.HEART,
        user_id="test_user"
    )
    
    response = mock_data_service.add_emoji_reaction(reaction)
    if response.success:
        print(f"✅ Added emoji reaction: {response.emoji_type}")
    else:
        print("❌ Failed to add emoji reaction")
        return False
    
    # Test analytics
    global_analytics = mock_data_service.get_global_analytics()
    print(f"✅ Global analytics - Total reactions: {global_analytics.total_reactions}")
    
    match_analytics = mock_data_service.get_match_analytics(1)
    if match_analytics:
        print(f"✅ Match analytics - Total reactions: {match_analytics.total_reactions}")
    else:
        print("❌ Failed to get match analytics")
        return False
    
    print("🎉 All mock data service tests passed!")
    return True

def test_models():
    """Test Pydantic models"""
    print("📋 Testing Pydantic Models...")
    
    try:
        # Test emoji reaction model
        reaction = EmojiReaction(
            match_id=1,
            emoji_type=EmojiType.FIRE,
            user_id="test_user_123"
        )
        print(f"✅ EmojiReaction model: {reaction.emoji_type}")
        
        # Test JSON serialization
        json_data = reaction.model_dump_json()
        parsed = json.loads(json_data)
        print(f"✅ JSON serialization works: {parsed['emoji_type']}")
        
        print("🎉 All model tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

async def run_tests():
    """Run all tests"""
    print("🏁 Starting Fan Engagement Backend Tests")
    print("=" * 50)
    
    # Test models
    if not test_models():
        return False
    
    print()
    
    # Test mock data service
    if not await test_mock_data_service():
        return False
    
    print()
    print("🎊 All tests completed successfully!")
    print("✨ The Fan Engagement Backend is ready to use!")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(run_tests())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)
