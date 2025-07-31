from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MatchBase(BaseModel):
    """Base match schema with common fields"""
    title: str = Field(..., description="Match title", min_length=1, max_length=200)
    home_team: str = Field(..., description="Home team name", min_length=1, max_length=100)
    away_team: str = Field(..., description="Away team name", min_length=1, max_length=100)
    home_score: int = Field(default=0, description="Home team score", ge=0)
    away_score: int = Field(default=0, description="Away team score", ge=0)
    status: str = Field(default="scheduled", description="Match status")
    description: Optional[str] = Field(None, description="Match description")
    start_time: Optional[datetime] = Field(None, description="Match start time")
    end_time: Optional[datetime] = Field(None, description="Match end time")

class MatchCreate(MatchBase):
    """Schema for creating a new match"""
    pass

class MatchUpdate(BaseModel):
    """Schema for updating an existing match"""
    title: Optional[str] = Field(None, description="Updated title", min_length=1, max_length=200)
    home_team: Optional[str] = Field(None, description="Updated home team", min_length=1, max_length=100)
    away_team: Optional[str] = Field(None, description="Updated away team", min_length=1, max_length=100)
    home_score: Optional[int] = Field(None, description="Updated home score", ge=0)
    away_score: Optional[int] = Field(None, description="Updated away score", ge=0)
    status: Optional[str] = Field(None, description="Updated status")
    description: Optional[str] = Field(None, description="Updated description")
    start_time: Optional[datetime] = Field(None, description="Updated start time")
    end_time: Optional[datetime] = Field(None, description="Updated end time")
    is_live: Optional[bool] = Field(None, description="Updated live status")
    viewer_count: Optional[int] = Field(None, description="Updated viewer count", ge=0)

class MatchResponse(MatchBase):
    """Schema for match API responses"""
    id: int = Field(..., description="Unique identifier")
    is_live: bool = Field(..., description="Whether the match is currently live")
    viewer_count: int = Field(..., description="Current viewer count")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
