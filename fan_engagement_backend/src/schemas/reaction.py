from pydantic import BaseModel, Field
from datetime import datetime

class ReactionBase(BaseModel):
    """Base reaction schema with common fields"""
    match_id: int = Field(..., description="ID of the match being reacted to", gt=0)
    emoji_id: int = Field(..., description="ID of the emoji being used", gt=0)
    user_session: str = Field(..., description="User session identifier", min_length=1, max_length=100)

class ReactionCreate(ReactionBase):
    """Schema for creating a new reaction"""
    pass

class ReactionResponse(ReactionBase):
    """Schema for reaction API responses"""
    id: int = Field(..., description="Unique identifier")
    timestamp: datetime = Field(..., description="Reaction timestamp")
    
    class Config:
        from_attributes = True
