from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Reaction(Base):
    """
    Reaction model for storing user emoji reactions to matches.
    Links users' emoji reactions to specific matches with timestamps.
    """
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    emoji_id = Column(Integer, ForeignKey("emojis.id"), nullable=False, index=True)
    user_session = Column(String(100), nullable=False)  # Session ID for anonymous users
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    match = relationship("Match", backref="reactions")
    emoji = relationship("Emoji", backref="reactions")
    
    def __repr__(self):
        return f"<Reaction(id={self.id}, match_id={self.match_id}, emoji_id={self.emoji_id})>"
