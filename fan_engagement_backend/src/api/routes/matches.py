from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...models.database import get_db
from ...models.match import Match
from ...schemas.match import MatchCreate, MatchResponse, MatchUpdate

router = APIRouter(prefix="/matches", tags=["matches"])

# PUBLIC_INTERFACE
@router.get("/", response_model=List[MatchResponse])
def get_matches(
    skip: int = 0, 
    limit: int = 100, 
    live_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Retrieve all matches with optional filtering.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        live_only: Filter for live matches only
        db: Database session
        
    Returns:
        List of match objects
    """
    query = db.query(Match)
    if live_only:
        query = query.filter(Match.is_live == True)
    matches = query.offset(skip).limit(limit).all()
    return matches

# PUBLIC_INTERFACE
@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific match by ID.
    
    Args:
        match_id: Unique identifier for the match
        db: Database session
        
    Returns:
        Match object
        
    Raises:
        HTTPException: 404 if match not found
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    return match

# PUBLIC_INTERFACE
@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    """
    Create a new match.
    
    Args:
        match: Match creation data
        db: Database session
        
    Returns:
        Created match object
    """
    db_match = Match(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

# PUBLIC_INTERFACE
@router.put("/{match_id}", response_model=MatchResponse)
def update_match(match_id: int, match_update: MatchUpdate, db: Session = Depends(get_db)):
    """
    Update an existing match.
    
    Args:
        match_id: Unique identifier for the match
        match_update: Updated match data
        db: Database session
        
    Returns:
        Updated match object
        
    Raises:
        HTTPException: 404 if match not found
    """
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if not db_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Update fields
    update_data = match_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_match, field, value)
    
    db.commit()
    db.refresh(db_match)
    return db_match
