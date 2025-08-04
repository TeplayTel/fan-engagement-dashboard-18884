<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Optional

from ...models.database import get_db
from ...models.reaction import Reaction
from ...models.match import Match
from ...models.emoji import Emoji
from ...schemas.analytics import AnalyticsResponse, ReactionStats
from ...schemas.emoji import EmojiResponse
=======
from fastapi import APIRouter, HTTPException
from src.models.schemas import MatchAnalytics, GlobalAnalytics
from src.services.database_service import database_service
>>>>>>> cga-cg3c87e1d1

router = APIRouter(prefix="/analytics", tags=["analytics"])

# PUBLIC_INTERFACE
<<<<<<< HEAD
@router.get("/match/{match_id}", response_model=AnalyticsResponse)
def get_match_analytics(
    match_id: int,
    hours_back: Optional[int] = 24,
    db: Session = Depends(get_db)
):
    """
    Get live analytics for a specific match.
    
    Args:
        match_id: Unique identifier for the match
        hours_back: Number of hours to look back for analytics (default: 24)
        db: Database session
        
    Returns:
        Analytics data including reaction counts, user stats, and emoji breakdown
=======
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
    return database_service.get_global_analytics()

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
>>>>>>> cga-cg3c87e1d1
        
    Raises:
        HTTPException: 404 if match not found
    """
<<<<<<< HEAD
    # Verify match exists
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours_back)
    
    # Get total reactions in time range
    total_reactions = db.query(func.count(Reaction.id)).filter(
        Reaction.match_id == match_id,
        Reaction.timestamp >= start_time
    ).scalar() or 0
    
    # Get unique users count
    unique_users = db.query(func.count(func.distinct(Reaction.user_session))).filter(
        Reaction.match_id == match_id,
        Reaction.timestamp >= start_time
    ).scalar() or 0
    
    # Get reaction stats by emoji
    reaction_counts = db.query(
        Emoji,
        func.count(Reaction.id).label('count')
    ).join(
        Reaction, Emoji.id == Reaction.emoji_id
    ).filter(
        Reaction.match_id == match_id,
        Reaction.timestamp >= start_time
    ).group_by(Emoji.id).order_by(desc('count')).all()
    
    # Calculate percentages and create reaction stats
    reaction_stats = []
    for emoji, count in reaction_counts:
        percentage = (count / total_reactions * 100) if total_reactions > 0 else 0
        reaction_stats.append(ReactionStats(
            emoji=EmojiResponse.from_orm(emoji),
            count=count,
            percentage=round(percentage, 2)
        ))
    
    return AnalyticsResponse(
        match_id=match_id,
        total_reactions=total_reactions,
        unique_users=unique_users,
        reaction_stats=reaction_stats,
        time_range={
            "start": start_time,
            "end": end_time
        },
        additional_metrics={
            "avg_reactions_per_user": round(total_reactions / unique_users, 2) if unique_users > 0 else 0,
            "match_status": match.status,
            "is_live": match.is_live,
            "viewer_count": match.viewer_count
        }
    )

# PUBLIC_INTERFACE
@router.get("/global", response_model=dict)
def get_global_analytics(
    hours_back: Optional[int] = 24,
    db: Session = Depends(get_db)
):
    """
    Get global analytics across all matches.
    
    Args:
        hours_back: Number of hours to look back for analytics (default: 24)
        db: Database session
        
    Returns:
        Global analytics data including overall stats and top emojis
    """
    # Calculate time range
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours_back)
    
    # Get total reactions across all matches
    total_reactions = db.query(func.count(Reaction.id)).filter(
        Reaction.timestamp >= start_time
    ).scalar() or 0
    
    # Get unique users across all matches
    unique_users = db.query(func.count(func.distinct(Reaction.user_session))).filter(
        Reaction.timestamp >= start_time
    ).scalar() or 0
    
    # Get active matches count
    active_matches = db.query(func.count(Match.id)).filter(
        Match.is_live == True
    ).scalar() or 0
    
    # Get top emojis globally
    top_emojis = db.query(
        Emoji.name,
        Emoji.unicode_char,
        func.count(Reaction.id).label('count')
    ).join(
        Reaction, Emoji.id == Reaction.emoji_id
    ).filter(
        Reaction.timestamp >= start_time
    ).group_by(Emoji.id, Emoji.name, Emoji.unicode_char).order_by(desc('count')).limit(10).all()
    
    return {
        "time_range": {
            "start": start_time,
            "end": end_time
        },
        "total_reactions": total_reactions,
        "unique_users": unique_users,
        "active_matches": active_matches,
        "avg_reactions_per_user": round(total_reactions / unique_users, 2) if unique_users > 0 else 0,
        "top_emojis": [
            {
                "name": emoji.name,
                "unicode_char": emoji.unicode_char,
                "count": count
            }
            for emoji, count in top_emojis
        ]
=======
    # Check if match exists
    match = database_service.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    analytics = database_service.get_match_analytics(match_id)
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
    global_analytics = database_service.get_global_analytics()
    
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
>>>>>>> cga-cg3c87e1d1
    }
