from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class EmojiBase(BaseModel):
    """Base emoji schema with common fields"""
    name: str = Field(..., description="Unique name for the emoji", min_length=1, max_length=50)
    unicode_char: str = Field(..., description="Unicode character representation", min_length=1, max_length=10)
    category: str = Field(default="general", description="Category classification", max_length=50)

class EmojiCreate(EmojiBase):
    """Schema for creating a new emoji"""
    is_active: bool = Field(default=True, description="Whether the emoji is active")

class EmojiUpdate(BaseModel):
    """Schema for updating an existing emoji"""
    name: Optional[str] = Field(None, description="Updated name", min_length=1, max_length=50)
    unicode_char: Optional[str] = Field(None, description="Updated unicode character", min_length=1, max_length=10)
    category: Optional[str] = Field(None, description="Updated category", max_length=50)
    is_active: Optional[bool] = Field(None, description="Updated active status")

class EmojiResponse(EmojiBase):
    """Schema for emoji API responses"""
    id: int = Field(..., description="Unique identifier")
    is_active: bool = Field(..., description="Whether the emoji is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True
