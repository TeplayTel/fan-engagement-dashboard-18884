from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from datetime import datetime
from src.models.schemas import Match, MatchStatus
from src.services.mock_data import mock_data_service

router = APIRouter(prefix="/matches", tags=["matches"])

# PUBLIC_INTERFACE
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
    
    matches = mock_data_service.get_matches(filters)
    
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
        
    Raises:
        HTTPException: 404 if match not found
    """
    match = mock_data_service.get_match_by_id(match_id)
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
    return mock_data_service.get_matches({"status": MatchStatus.LIVE})

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
    upcoming_matches = mock_data_service.get_matches({"status": MatchStatus.UPCOMING})
    # Sort by start time
    upcoming_matches.sort(key=lambda x: x.start_time)
    return upcoming_matches[:limit]
