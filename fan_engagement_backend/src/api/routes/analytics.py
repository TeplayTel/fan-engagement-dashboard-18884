from fastapi import APIRouter, HTTPException
from src.models.schemas import MatchAnalytics, GlobalAnalytics
from src.services.mock_data import mock_data_service

router = APIRouter(prefix="/analytics", tags=["analytics"])

# PUBLIC_INTERFACE
@router.get("/global", response_model=GlobalAnalytics)
async def get_global_analytics():
    """
    Get global analytics data across all matches and users.
    
    Returns comprehensive analytics including:
    - Total users and reactions
    - Active matches count
    - Top matches by engagement
    - Emoji distribution
    - Peak activity times
    
    Returns:
        GlobalAnalytics object with comprehensive platform statistics
    """
    return mock_data_service.get_global_analytics()

# PUBLIC_INTERFACE
@router.get("/match/{match_id}", response_model=MatchAnalytics)
async def get_match_analytics(match_id: int):
    """
    Get detailed analytics for a specific match.
    
    Returns match-specific analytics including:
    - Total reactions count
    - Emoji breakdown and distribution  
    - Reactions per minute timeline
    - Top performing emojis with percentages
    
    Args:
        match_id: The unique identifier of the match
        
    Returns:
        MatchAnalytics object with detailed match engagement data
        
    Raises:
        HTTPException: 404 if match not found
    """
    # Check if match exists
    match = mock_data_service.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    analytics = mock_data_service.get_match_analytics(match_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found for this match")
    
    return analytics

# PUBLIC_INTERFACE
@router.get("/summary", response_model=dict)
async def get_analytics_summary():
    """
    Get a quick summary of key analytics metrics.
    
    Returns a simplified analytics overview suitable for dashboards
    and quick status checks.
    
    Returns:
        Dictionary containing key metrics like total reactions, 
        active users, and current activity level
    """
    global_analytics = mock_data_service.get_global_analytics()
    
    return {
        "total_reactions": global_analytics.total_reactions,
        "total_users": global_analytics.total_users,
        "active_matches": global_analytics.active_matches,
        "reactions_last_hour": global_analytics.reactions_last_hour,
        "most_popular_emoji": max(
            global_analytics.emoji_distribution.items(),
            key=lambda x: x[1],
            default=("❤️", 0)
        )[0],
        "connection_count": 0  # Will be updated by websocket manager
    }
