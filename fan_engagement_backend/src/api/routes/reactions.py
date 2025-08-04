<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...models.database import get_db
from ...models.reaction import Reaction
from ...models.match import Match
from ...models.emoji import Emoji
from ...schemas.reaction import ReactionCreate, ReactionResponse
=======
from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.models.schemas import EmojiReaction, EmojiReactionResponse, EmojiType
from src.services.database_service import database_service
from src.services.websocket_manager import connection_manager
>>>>>>> cga-cg3c87e1d1

router = APIRouter(prefix="/reactions", tags=["reactions"])

# PUBLIC_INTERFACE
<<<<<<< HEAD
@router.post("/", response_model=ReactionResponse, status_code=status.HTTP_201_CREATED)
def create_reaction(reaction: ReactionCreate, db: Session = Depends(get_db)):
    """
    Create a new emoji reaction for a match.
    
    Args:
        reaction: Reaction creation data
        db: Database session
        
    Returns:
        Created reaction object
        
    Raises:
        HTTPException: 404 if match or emoji not found
    """
    # Verify match exists
    match = db.query(Match).filter(Match.id == reaction.match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Verify emoji exists and is active
    emoji = db.query(Emoji).filter(
        Emoji.id == reaction.emoji_id, 
        Emoji.is_active == True
    ).first()
    if not emoji:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emoji not found or inactive"
        )
    
    db_reaction = Reaction(**reaction.dict())
    db.add(db_reaction)
    db.commit()
    db.refresh(db_reaction)
    return db_reaction

# PUBLIC_INTERFACE
@router.get("/match/{match_id}", response_model=List[ReactionResponse])
def get_match_reactions(
    match_id: int, 
    skip: int = 0, 
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """
    Get all reactions for a specific match.
    
    Args:
        match_id: Unique identifier for the match
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of reaction objects for the match
=======
@router.post("/emoji_reaction", response_model=EmojiReactionResponse)
async def submit_emoji_reaction(
    reaction: EmojiReaction,
    background_tasks: BackgroundTasks
):
    """
    Submit an emoji reaction for a match.
    
    This endpoint accepts emoji reactions from users and:
    1. Records the reaction in the system
    2. Updates global and match-specific analytics
    3. Broadcasts the reaction to all connected WebSocket clients
    
    Args:
        reaction: The emoji reaction data including match_id, emoji_type, and optional user_id
        
    Returns:
        EmojiReactionResponse with reaction details and confirmation
        
    Raises:
        HTTPException: 404 if match not found, 400 for invalid data
    """
    # Validate that the match exists
    match = database_service.get_match_by_id(reaction.match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Add the reaction
    reaction_response = database_service.add_emoji_reaction(reaction)
    
    # Prepare broadcast data
    broadcast_data = {
        "match_id": reaction.match_id,
        "emoji": reaction.emoji_type.value,
        "user_id": reaction.user_id,
        "timestamp": reaction_response.timestamp.isoformat(),
        "match_name": f"{match.home_team.name} vs {match.away_team.name}"
    }
    
    # Broadcast the reaction asynchronously
    background_tasks.add_task(
        connection_manager.broadcast_reaction,
        broadcast_data
    )
    
    # Also broadcast updated analytics
    analytics = database_service.get_global_analytics()
    background_tasks.add_task(
        connection_manager.broadcast_analytics_update,
        analytics.model_dump()
    )
    
    return reaction_response

# PUBLIC_INTERFACE
@router.get("/emojis", response_model=list)
async def get_available_emojis():
    """
    Get all available emoji types for reactions.
    
    Returns:
        List of available emoji types with their values
    """
    return [{"name": emoji.name, "value": emoji.value} for emoji in EmojiType]

# PUBLIC_INTERFACE
@router.get("/match/{match_id}/recent", response_model=list)
async def get_recent_reactions(match_id: int, limit: int = 10):
    """
    Get recent emoji reactions for a specific match.
    
    Args:
        match_id: The match ID to get reactions for
        limit: Maximum number of recent reactions to return
        
    Returns:
        List of recent emoji reactions for the match
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
    
    reactions = db.query(Reaction).filter(
        Reaction.match_id == match_id
    ).offset(skip).limit(limit).all()
    
    return reactions
=======
    # Validate match exists
    match = database_service.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Get recent reactions from database
    try:
        from src.database.connection import DatabaseSession
        from src.database.models import Reaction, Emoji, Match
        
        with DatabaseSession() as db:
            # Get the actual match from database to get UUID
            db_match = None
            if isinstance(match_id, int):
                matches = db.query(Match).all()
                if match_id <= len(matches):
                    db_match = matches[match_id - 1]
            
            if db_match:
                recent_reactions = db.query(Reaction).join(Emoji).filter(
                    Reaction.match_id == db_match.id
                ).order_by(Reaction.reaction_timestamp.desc()).limit(limit).all()
                
                match_reactions = [
                    {
                        "emoji": reaction.emoji.unicode_symbol,
                        "user_id": reaction.user_session_id,
                        "timestamp": reaction.reaction_timestamp.isoformat()
                    }
                    for reaction in recent_reactions
                ]
                
                return match_reactions
            else:
                return []
    except Exception:
        # Fallback to empty list if there's an error
        return []
>>>>>>> cga-cg3c87e1d1
