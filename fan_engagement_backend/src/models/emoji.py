from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class Emoji(Base):
    """
    Emoji model for storing emoji assets and metadata.
    Represents individual emoji options available for user reactions.
    """
    __tablename__ = "emojis"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    unicode_char = Column(String(10), nullable=False)
    category = Column(String(50), default="general")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Emoji(id={self.id}, name='{self.name}', unicode_char='{self.unicode_char}')>"
