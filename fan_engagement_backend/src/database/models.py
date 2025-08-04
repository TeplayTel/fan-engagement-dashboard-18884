"""
SQLAlchemy models for Fan Engagement Dashboard

This module defines all database models using SQLAlchemy ORM,
including relationships and constraints for the fan engagement system.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, CheckConstraint, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from .connection import Base


class TimestampMixin:
    """
    Mixin class for adding timestamp fields to models
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class Team(Base, TimestampMixin):
    """
    Team model representing football teams
    """
    __tablename__ = "teams"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    short_name: Mapped[str] = mapped_column(String(10), nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    primary_color: Mapped[str] = mapped_column(String(7), default="#000000", nullable=False)
    secondary_color: Mapped[str] = mapped_column(String(7), default="#FFFFFF", nullable=False)
    
    # Relationships
    home_matches: Mapped[List["Match"]] = relationship(
        "Match", 
        foreign_keys="[Match.home_team_id]",
        back_populates="home_team"
    )
    away_matches: Mapped[List["Match"]] = relationship(
        "Match", 
        foreign_keys="[Match.away_team_id]",
        back_populates="away_team"
    )
    reactions: Mapped[List["Reaction"]] = relationship(
        "Reaction", 
        back_populates="team",
        cascade="all, delete-orphan"
    )
    analytics: Mapped[List["AnalyticsAggregate"]] = relationship(
        "AnalyticsAggregate", 
        back_populates="team",
        cascade="all, delete-orphan"
    )
    match_events: Mapped[List["MatchEvent"]] = relationship(
        "MatchEvent", 
        back_populates="team",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Team(id={self.id}, name='{self.name}', short_name='{self.short_name}')>"


class Match(Base, TimestampMixin):
    """
    Match model representing football matches
    """
    __tablename__ = "matches"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    home_team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )
    away_team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False
    )
    match_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="scheduled", nullable=False)
    home_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    away_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    competition: Mapped[str] = mapped_column(String(100), nullable=False)
    venue: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    match_duration: Mapped[int] = mapped_column(Integer, default=90, nullable=False)
    video_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    home_team: Mapped["Team"] = relationship(
        "Team", 
        foreign_keys=[home_team_id],
        back_populates="home_matches"
    )
    away_team: Mapped["Team"] = relationship(
        "Team", 
        foreign_keys=[away_team_id],
        back_populates="away_matches"
    )
    reactions: Mapped[List["Reaction"]] = relationship(
        "Reaction", 
        back_populates="match",
        cascade="all, delete-orphan"
    )
    analytics: Mapped[List["AnalyticsAggregate"]] = relationship(
        "AnalyticsAggregate", 
        back_populates="match",
        cascade="all, delete-orphan"
    )
    events: Mapped[List["MatchEvent"]] = relationship(
        "MatchEvent", 
        back_populates="match",
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("home_team_id != away_team_id", name="different_teams"),
        Index("idx_matches_status", "status"),
        Index("idx_matches_date", "match_date"),
        Index("idx_matches_home_team", "home_team_id"),
        Index("idx_matches_away_team", "away_team_id"),
    )
    
    def __repr__(self) -> str:
        return f"<Match(id={self.id}, status='{self.status}', score={self.home_score}-{self.away_score})>"


class Emoji(Base, TimestampMixin):
    """
    Emoji model representing available reaction emojis
    """
    __tablename__ = "emojis"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    unicode_symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    reactions: Mapped[List["Reaction"]] = relationship(
        "Reaction", 
        back_populates="emoji",
        cascade="all, delete-orphan"
    )
    analytics: Mapped[List["AnalyticsAggregate"]] = relationship(
        "AnalyticsAggregate", 
        back_populates="emoji",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Emoji(id={self.id}, name='{self.name}', symbol='{self.unicode_symbol}')>"


class Reaction(Base):
    """
    Reaction model representing user reactions during matches
    """
    __tablename__ = "reactions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False
    )
    emoji_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emojis.id", ondelete="CASCADE"),
        nullable=False
    )
    user_session_id: Mapped[str] = mapped_column(String(255), nullable=False)
    team_preference: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=True
    )
    reaction_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    match_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    x_position: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    y_position: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="reactions")
    emoji: Mapped["Emoji"] = relationship("Emoji", back_populates="reactions")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="reactions")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("x_position >= 0 AND x_position <= 1 OR x_position IS NULL", name="valid_x_position"),
        CheckConstraint("y_position >= 0 AND y_position <= 1 OR y_position IS NULL", name="valid_y_position"),
        Index("idx_reactions_match", "match_id"),
        Index("idx_reactions_emoji", "emoji_id"),
        Index("idx_reactions_timestamp", "reaction_timestamp"),
        Index("idx_reactions_session", "user_session_id"),
        Index("idx_reactions_team", "team_preference"),
    )
    
    def __repr__(self) -> str:
        return f"<Reaction(id={self.id}, match_id={self.match_id}, emoji_id={self.emoji_id})>"


class AnalyticsAggregate(Base, TimestampMixin):
    """
    Analytics aggregate model for performance optimization
    """
    __tablename__ = "analytics_aggregates"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False
    )
    emoji_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emojis.id", ondelete="CASCADE"),
        nullable=False
    )
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=True
    )
    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    time_period: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reaction_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="analytics")
    emoji: Mapped["Emoji"] = relationship("Emoji", back_populates="analytics")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="analytics")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "match_id", "emoji_id", "team_id", "aggregate_type", "time_period",
            name="unique_analytics_aggregate"
        ),
        Index("idx_analytics_match", "match_id"),
        Index("idx_analytics_time", "time_period"),
        Index("idx_analytics_type", "aggregate_type"),
    )
    
    def __repr__(self) -> str:
        return f"<AnalyticsAggregate(id={self.id}, type='{self.aggregate_type}', count={self.reaction_count})>"


class MatchEvent(Base):
    """
    Match event model for storing key match events
    """
    __tablename__ = "match_events"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False
    )
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_minute: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id"),
        nullable=True
    )
    player_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    match: Mapped["Match"] = relationship("Match", back_populates="events")
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="match_events")
    
    # Constraints
    __table_args__ = (
        Index("idx_match_events_match", "match_id"),
        Index("idx_match_events_minute", "event_minute"),
    )
    
    def __repr__(self) -> str:
        return f"<MatchEvent(id={self.id}, type='{self.event_type}', minute={self.event_minute})>"


# Database views (created via SQL, represented here for reference)
class MatchDetailsView:
    """
    Virtual model representing the match_details view
    This view combines match data with team information
    """
    pass


class ReactionAnalyticsView:
    """
    Virtual model representing the reaction_analytics view
    This view provides aggregated reaction statistics
    """
    pass


# Utility functions for model operations
def create_default_emojis() -> List[Emoji]:
    """
    Create default emoji set for the application
    
    Returns:
        List[Emoji]: List of default emoji models
    """
    default_emojis = [
        {"name": "goal", "unicode_symbol": "⚽", "category": "celebration"},
        {"name": "fire", "unicode_symbol": "🔥", "category": "excitement"},
        {"name": "heart", "unicode_symbol": "❤️", "category": "love"},
        {"name": "thumbs_up", "unicode_symbol": "👍", "category": "approval"},
        {"name": "thumbs_down", "unicode_symbol": "👎", "category": "disapproval"},
        {"name": "angry", "unicode_symbol": "😠", "category": "disappointment"},
        {"name": "sad", "unicode_symbol": "😢", "category": "disappointment"},
        {"name": "laugh", "unicode_symbol": "😂", "category": "amusement"},
        {"name": "surprised", "unicode_symbol": "😲", "category": "surprise"},
        {"name": "clap", "unicode_symbol": "👏", "category": "applause"},
        {"name": "facepalm", "unicode_symbol": "🤦", "category": "frustration"},
        {"name": "rocket", "unicode_symbol": "🚀", "category": "excitement"},
        {"name": "trophy", "unicode_symbol": "🏆", "category": "victory"},
        {"name": "lightning", "unicode_symbol": "⚡", "category": "energy"},
        {"name": "crown", "unicode_symbol": "👑", "category": "excellence"},
    ]
    
    return [Emoji(**emoji_data) for emoji_data in default_emojis]


def create_sample_teams() -> List[Team]:
    """
    Create sample teams for development/testing
    
    Returns:
        List[Team]: List of sample team models
    """
    sample_teams = [
        {
            "name": "Arsenal",
            "short_name": "ARS",
            "logo_url": "/assets/teams/arsenal-logo.png",
            "primary_color": "#DC143C",
            "secondary_color": "#FFFFFF"
        },
        {
            "name": "Chelsea",
            "short_name": "CHE", 
            "logo_url": "/assets/teams/chelsea-logo.png",
            "primary_color": "#034694",
            "secondary_color": "#FFFFFF"
        },
        {
            "name": "Manchester United",
            "short_name": "MUN",
            "logo_url": "/assets/teams/manchester-united-logo.png",
            "primary_color": "#FF0000",
            "secondary_color": "#FFFFFF"
        },
        {
            "name": "Manchester City",
            "short_name": "MCI",
            "logo_url": "/assets/teams/manchester-city-logo.png",
            "primary_color": "#6CABDD",
            "secondary_color": "#FFFFFF"
        },
        {
            "name": "Liverpool",
            "short_name": "LIV",
            "logo_url": "/assets/teams/liverpool-logo.png",
            "primary_color": "#C8102E",
            "secondary_color": "#FFFFFF"
        }
    ]
    
    return [Team(**team_data) for team_data in sample_teams]
