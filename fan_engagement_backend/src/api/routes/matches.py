<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...models.database import get_db
from ...models.match import Match
from ...schemas.match import MatchCreate, MatchResponse, MatchUpdate
=======
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime
from src.models.schemas import Match, MatchStatus
from src.services.database_service import database_service
>>>>>>> cga-cg3c87e1d1

router = APIRouter(prefix="/matches", tags=["matches"])

# PUBLIC_INTERFACE
<<<<<<< HEAD
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
=======
@router.get("/", response_model=List[Match])
async def get_matches(
    status: Optional[MatchStatus] = Query(None, description="Filter matches by status (live, upcoming, completed)"),
    league: Optional[str] = Query(None, description="Filter matches by league name"),
    team: Optional[str] = Query(None, description="Filter matches by team name (partial match)"),
    date_from: Optional[datetime] = Query(None, description="Filter matches from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter matches until this date"),
    limit: Optional[int] = Query(None, description="Limit the number of results")
):
    """
    Get all matches with optional filtering.
    
    Returns a list of matches that can be filtered by:
    - Status: live, upcoming, completed
    - League: Premier League, Champions League, etc.
    - Team: Any team name (partial matching supported)
    - Date range: Filter by match date
    """
    filters = {}
    if status:
        filters["status"] = status
    if league:
        filters["league"] = league
    if team:
        filters["team"] = team
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    
    matches = database_service.get_matches(filters)
    
    if limit:
        matches = matches[:limit]
    
    return matches

# PUBLIC_INTERFACE
@router.get("/{match_id}", response_model=Match)
async def get_match(match_id: int):
    """
    Get a specific match by ID.
    
    Args:
        match_id: The unique identifier of the match
        
    Returns:
        Match details including teams, status, score, and venue information
>>>>>>> cga-cg3c87e1d1
        
    Raises:
        HTTPException: 404 if match not found
    """
<<<<<<< HEAD
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
=======
    match = database_service.get_match_by_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

# PUBLIC_INTERFACE
@router.get("/live/current", response_model=List[Match])
async def get_live_matches():
    """
    Get all currently live matches.
    
    Returns:
        List of matches that are currently being played live
    """
    return database_service.get_matches({"status": MatchStatus.LIVE})

# PUBLIC_INTERFACE
@router.get("/upcoming/next", response_model=List[Match])
async def get_upcoming_matches(limit: int = Query(5, description="Number of upcoming matches to return")):
    """
    Get upcoming matches ordered by start time.
    
    Args:
        limit: Maximum number of matches to return (default: 5)
        
    Returns:
        List of upcoming matches sorted by start time
    """
    upcoming_matches = database_service.get_matches({"status": MatchStatus.UPCOMING})
    # Sort by start time
    upcoming_matches.sort(key=lambda x: x.start_time)
    return upcoming_matches[:limit]
>>>>>>> cga-cg3c87e1d1
