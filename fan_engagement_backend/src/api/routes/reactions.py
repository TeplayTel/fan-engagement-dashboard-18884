from fastapi import APIRouter, HTTPException, BackgroundTasks
from src.models.schemas import EmojiReaction, EmojiReactionResponse, EmojiType
from src.services.mock_data import mock_data_service
from src.services.websocket_manager import connection_manager

router = APIRouter(prefix="/reactions", tags=["reactions"])

# PUBLIC_INTERFACE
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
    match = mock_data_service.get_match_by_id(reaction.match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Add the reaction
    reaction_response = mock_data_service.add_emoji_reaction(reaction)
    
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
    analytics = mock_data_service.get_global_analytics()
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
        
    Raises:
        HTTPException: 404 if match not found
    """
    # Validate match exists
    match = mock_data_service.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Filter reactions for this match (in a real app, this would be from database)
    match_reactions = [
        {
            "emoji": reaction.emoji_type.value,
            "user_id": reaction.user_id,
            "timestamp": reaction.timestamp.isoformat() if reaction.timestamp else None
        }
        for reaction in mock_data_service.reactions 
        if reaction.match_id == match_id
    ]
    
    # Return most recent reactions (reverse chronological order)
    return match_reactions[-limit:][::-1]
