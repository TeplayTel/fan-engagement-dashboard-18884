from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any
from .emoji import EmojiResponse

class ReactionStats(BaseModel):
    """Statistics for emoji reactions"""
    emoji: EmojiResponse = Field(..., description="Emoji information")
    count: int = Field(..., description="Number of reactions", ge=0)
    percentage: float = Field(..., description="Percentage of total reactions", ge=0, le=100)

class AnalyticsResponse(BaseModel):
    """Analytics data response schema"""
    match_id: int = Field(..., description="Match ID for analytics", gt=0)
    total_reactions: int = Field(..., description="Total number of reactions", ge=0)
    unique_users: int = Field(..., description="Number of unique users", ge=0)
    reaction_stats: List[ReactionStats] = Field(..., description="Breakdown by emoji")
    time_range: Dict[str, datetime] = Field(..., description="Analytics time range")
    additional_metrics: Dict[str, Any] = Field(default_factory=dict, description="Additional analytics data")
