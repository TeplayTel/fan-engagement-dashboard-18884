from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MatchStatus(str, Enum):
    LIVE = "live"
    UPCOMING = "upcoming"
    COMPLETED = "completed"

class EmojiType(str, Enum):
    HEART = "❤️"
    FIRE = "🔥"
    CLAP = "👏"
    THUMBS_UP = "👍"
    GOAL = "⚽"
    CELEBRATION = "🎉"
    ANGRY = "😠"
    SAD = "😢"

class Team(BaseModel):
    """Team information model"""
    id: int
    name: str
    short_name: str
    logo_url: str
    primary_color: str

class Match(BaseModel):
    """Match information model"""
    id: int
    home_team: Team
    away_team: Team
    status: MatchStatus
    start_time: datetime
    league: str
    score: Optional[Dict[str, int]] = None  # {"home": 2, "away": 1}
    match_time: Optional[str] = None  # "45' + 2", "HT", "FT"
    venue: str

class EmojiReaction(BaseModel):
    """Emoji reaction model"""
    match_id: int
    emoji_type: EmojiType
    user_id: Optional[str] = None
    timestamp: Optional[datetime] = None

class EmojiReactionResponse(BaseModel):
    """Response model for emoji reaction"""
    id: int
    match_id: int
    emoji_type: EmojiType
    user_id: Optional[str]
    timestamp: datetime
    success: bool = True
    message: str = "Reaction recorded successfully"

class MatchAnalytics(BaseModel):
    """Match analytics model"""
    match_id: int
    total_reactions: int
    emoji_breakdown: Dict[str, int]  # {"❤️": 150, "🔥": 89, ...}
    reactions_per_minute: List[Dict[str, Any]]  # [{"minute": 45, "count": 23}, ...]
    top_emojis: List[Dict[str, Any]]  # [{"emoji": "❤️", "count": 150, "percentage": 35.2}, ...]

class GlobalAnalytics(BaseModel):
    """Global analytics model"""
    total_users: int
    total_reactions: int
    active_matches: int
    top_matches: List[Dict[str, Any]]
    emoji_distribution: Dict[str, int]
    reactions_last_hour: int
    peak_activity_time: str

class MatchFilter(BaseModel):
    """Match filter parameters"""
    status: Optional[MatchStatus] = None
    league: Optional[str] = None
    team: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str  # "reaction", "analytics_update", "match_update"
    data: Dict[str, Any]
    timestamp: datetime
