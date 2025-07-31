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

router = APIRouter(prefix="/analytics", tags=["analytics"])

# PUBLIC_INTERFACE
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
        
    Raises:
        HTTPException: 404 if match not found
    """
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
    }
