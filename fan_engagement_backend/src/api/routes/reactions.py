from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...models.database import get_db
from ...models.reaction import Reaction
from ...models.match import Match
from ...models.emoji import Emoji
from ...schemas.reaction import ReactionCreate, ReactionResponse

router = APIRouter(prefix="/reactions", tags=["reactions"])

# PUBLIC_INTERFACE
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
    
    reactions = db.query(Reaction).filter(
        Reaction.match_id == match_id
    ).offset(skip).limit(limit).all()
    
    return reactions
