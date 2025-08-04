"""
Database service for Fan Engagement Backend

This service provides database operations for teams, matches, reactions, 
emojis, and analytics using SQLAlchemy ORM with PostgreSQL.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from src.database.connection import DatabaseSession
from src.database.models import (
    Team, Match, Emoji, Reaction,
    create_default_emojis, create_sample_teams
)
from src.models.schemas import (
    Match as MatchSchema, Team as TeamSchema, MatchStatus, EmojiType,
    EmojiReaction, EmojiReactionResponse, MatchAnalytics, GlobalAnalytics
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Database service class for handling all database operations
    """
    
    def __init__(self):
        """Initialize the database service"""
        self.logger = logger
        self._ensure_initial_data()
    
    def _ensure_initial_data(self):
        """Ensure initial data exists in the database"""
        try:
            # First ensure tables exist
            from src.database.connection import db_manager
            db_manager.create_tables()
            self.logger.info("Database tables ensured")
            
            with DatabaseSession() as db:
                # Check if we have emojis
                try:
                    emoji_count = db.query(Emoji).count()
                    self.logger.info(f"Found {emoji_count} existing emojis")
                except Exception as e:
                    self.logger.warning(f"Could not count emojis: {e}")
                    emoji_count = 0
                
                if emoji_count == 0:
                    self.logger.info("No emojis found, creating default emojis...")
                    default_emojis = create_default_emojis()
                    for emoji in default_emojis:
                        db.add(emoji)
                    db.commit()
                    self.logger.info(f"Created {len(default_emojis)} default emojis")
                
                # Check if we have teams
                try:
                    team_count = db.query(Team).count()
                    self.logger.info(f"Found {team_count} existing teams")
                except Exception as e:
                    self.logger.warning(f"Could not count teams: {e}")
                    team_count = 0
                
                if team_count == 0:
                    self.logger.info("No teams found, creating sample teams...")
                    sample_teams = create_sample_teams()
                    for team in sample_teams:
                        db.add(team)
                    db.commit()
                    self.logger.info(f"Created {len(sample_teams)} sample teams")
                
                # Check if we have matches (create them separately)
                try:
                    match_count = db.query(Match).count()
                    self.logger.info(f"Found {match_count} existing matches")
                except Exception as e:
                    self.logger.warning(f"Could not count matches: {e}")
                    match_count = 0
                
                if match_count == 0:
                    self.logger.info("No matches found, creating sample matches...")
                    self._create_sample_matches(db)
                    
        except Exception as e:
            self.logger.error(f"Error ensuring initial data: {e}")
    
    def _create_sample_matches(self, db: Session):
        """Create sample matches for development"""
        try:
            teams = db.query(Team).limit(8).all()
            if len(teams) < 4:
                self.logger.warning("Not enough teams to create sample matches")
                return
            
            now = datetime.now()
            matches_data = [
                {
                    "home_team": teams[0], "away_team": teams[1],
                    "match_date": now - timedelta(hours=1),
                    "status": "live", "home_score": 2, "away_score": 1,
                    "competition": "Premier League", "venue": "Emirates Stadium"
                },
                {
                    "home_team": teams[2], "away_team": teams[3],
                    "match_date": now + timedelta(hours=2),
                    "status": "scheduled", "home_score": 0, "away_score": 0,
                    "competition": "Premier League", "venue": "Old Trafford"
                },
                {
                    "home_team": teams[4], "away_team": teams[1],
                    "match_date": now - timedelta(days=1),
                    "status": "completed", "home_score": 3, "away_score": 0,
                    "competition": "Premier League", "venue": "Etihad Stadium"
                }
            ]
            
            for match_data in matches_data:
                match = Match(
                    home_team_id=match_data["home_team"].id,
                    away_team_id=match_data["away_team"].id,
                    match_date=match_data["match_date"],
                    status=match_data["status"],
                    home_score=match_data["home_score"],
                    away_score=match_data["away_score"],
                    competition=match_data["competition"],
                    venue=match_data["venue"]
                )
                db.add(match)
            
            db.commit()
            self.logger.info("Created sample matches")
            
        except Exception as e:
            self.logger.error(f"Error creating sample matches: {e}")
            db.rollback()
    
    # PUBLIC_INTERFACE
    def get_matches(self, filters: Optional[Dict[str, Any]] = None) -> List[MatchSchema]:
        """
        Get matches with optional filtering
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List of match schemas
        """
        try:
            with DatabaseSession() as db:
                # Get all matches with their teams loaded
                matches = db.query(Match).all()
                self.logger.info(f"Retrieved {len(matches)} matches from database")
                
                # Apply filters if provided
                if filters:
                    filtered_matches = []
                    for match in matches:
                        include_match = True
                        
                        if filters.get("status"):
                            status_map = {
                                MatchStatus.LIVE: "live",
                                MatchStatus.UPCOMING: "scheduled", 
                                MatchStatus.COMPLETED: "completed"
                            }
                            db_status = status_map.get(filters["status"], filters["status"])
                            if match.status != db_status:
                                include_match = False
                        
                        if filters.get("league") and include_match:
                            if filters["league"].lower() not in match.competition.lower():
                                include_match = False
                        
                        if filters.get("team") and include_match:
                            team_filter = filters["team"].lower()
                            if (team_filter not in match.home_team.name.lower() and 
                                team_filter not in match.away_team.name.lower()):
                                include_match = False
                        
                        if filters.get("date_from") and include_match:
                            if match.match_date < filters["date_from"]:
                                include_match = False
                        
                        if filters.get("date_to") and include_match:
                            if match.match_date > filters["date_to"]:
                                include_match = False
                        
                        if include_match:
                            filtered_matches.append(match)
                    
                    matches = filtered_matches
                
                # Sort by match date (most recent first)
                matches.sort(key=lambda x: x.match_date, reverse=True)
                
                result = [self._convert_match_to_schema(match) for match in matches]
                self.logger.info(f"Converted {len(result)} matches to schema")
                return result
                
        except Exception as e:
            self.logger.error(f"Error getting matches: {e}")
            return []
    
    # PUBLIC_INTERFACE  
    def get_match_by_id(self, match_id: int) -> Optional[MatchSchema]:
        """
        Get a specific match by ID
        
        Args:
            match_id: The match ID
            
        Returns:
            Match schema or None if not found
        """
        try:
            with DatabaseSession() as db:
                # Convert int ID to UUID if needed
                if isinstance(match_id, int):
                    # For backwards compatibility with mock data, 
                    # we'll query by a different approach
                    matches = db.query(Match).all()
                    if match_id <= len(matches):
                        match = matches[match_id - 1]  # 1-based indexing
                    else:
                        return None
                else:
                    match = db.query(Match).filter(Match.id == match_id).first()
                
                if match:
                    return self._convert_match_to_schema(match)
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting match by ID {match_id}: {e}")
            return None
    
    # PUBLIC_INTERFACE
    def add_emoji_reaction(self, reaction: EmojiReaction) -> EmojiReactionResponse:
        """
        Add an emoji reaction to a match
        
        Args:
            reaction: The emoji reaction data
            
        Returns:
            Emoji reaction response
        """
        try:
            with DatabaseSession() as db:
                # Get the emoji by type
                emoji_map = {
                    EmojiType.HEART: "heart",
                    EmojiType.FIRE: "fire", 
                    EmojiType.CLAP: "clap",
                    EmojiType.THUMBS_UP: "thumbs_up",
                    EmojiType.GOAL: "goal",
                    EmojiType.CELEBRATION: "celebration",
                    EmojiType.ANGRY: "angry",
                    EmojiType.SAD: "sad"
                }
                
                emoji_name = emoji_map.get(reaction.emoji_type, "heart")
                emoji = db.query(Emoji).filter(Emoji.name == emoji_name).first()
                
                if not emoji:
                    # Create emoji if it doesn't exist
                    emoji = Emoji(
                        name=emoji_name,
                        unicode_symbol=reaction.emoji_type.value,
                        category="general"
                    )
                    db.add(emoji)
                    db.flush()
                
                # Get match to validate it exists
                match = None
                if isinstance(reaction.match_id, int):
                    matches = db.query(Match).all()
                    if reaction.match_id <= len(matches):
                        match = matches[reaction.match_id - 1]
                else:
                    match = db.query(Match).filter(Match.id == reaction.match_id).first()
                
                if not match:
                    raise ValueError(f"Match with ID {reaction.match_id} not found")
                
                # Create the reaction
                db_reaction = Reaction(
                    match_id=match.id,
                    emoji_id=emoji.id,
                    user_session_id=reaction.user_id or "anonymous",
                    reaction_timestamp=reaction.timestamp or datetime.now()
                )
                
                db.add(db_reaction)
                db.commit()
                
                return EmojiReactionResponse(
                    id=1,  # For compatibility
                    match_id=reaction.match_id,
                    emoji_type=reaction.emoji_type,
                    user_id=reaction.user_id,
                    timestamp=db_reaction.reaction_timestamp,
                    success=True,
                    message="Reaction recorded successfully"
                )
                
        except Exception as e:
            self.logger.error(f"Error adding emoji reaction: {e}")
            return EmojiReactionResponse(
                id=0,
                match_id=reaction.match_id,
                emoji_type=reaction.emoji_type,
                user_id=reaction.user_id,
                timestamp=datetime.now(),
                success=False,
                message=f"Error recording reaction: {str(e)}"
            )
    
    # PUBLIC_INTERFACE
    def get_match_analytics(self, match_id: int) -> Optional[MatchAnalytics]:
        """
        Get analytics for a specific match
        
        Args:
            match_id: The match ID
            
        Returns:
            Match analytics or None if not found
        """
        try:
            with DatabaseSession() as db:
                # Get match
                match = None
                if isinstance(match_id, int):
                    matches = db.query(Match).all()
                    if match_id <= len(matches):
                        match = matches[match_id - 1]
                else:
                    match = db.query(Match).filter(Match.id == match_id).first()
                
                if not match:
                    return None
                
                # Get reaction counts for this match
                reaction_counts = db.query(
                    Emoji.unicode_symbol,
                    func.count(Reaction.id)
                ).join(
                    Reaction, Reaction.emoji_id == Emoji.id
                ).filter(
                    Reaction.match_id == match.id
                ).group_by(
                    Emoji.unicode_symbol
                ).all()
                
                # Build emoji breakdown
                emoji_breakdown = {}
                total_reactions = 0
                for emoji_symbol, count in reaction_counts:
                    emoji_breakdown[emoji_symbol] = count
                    total_reactions += count
                
                # Create reactions per minute (simplified)
                reactions_per_minute = []
                for minute in range(0, 90, 10):
                    count = db.query(func.count(Reaction.id)).filter(
                        and_(
                            Reaction.match_id == match.id,
                            Reaction.match_minute >= minute,
                            Reaction.match_minute < minute + 10
                        )
                    ).scalar() or 0
                    reactions_per_minute.append({
                        "minute": minute,
                        "count": count
                    })
                
                # Create top emojis list
                top_emojis = []
                for emoji_symbol, count in sorted(reaction_counts, key=lambda x: x[1], reverse=True)[:5]:
                    percentage = (count / total_reactions * 100) if total_reactions > 0 else 0
                    top_emojis.append({
                        "emoji": emoji_symbol,
                        "count": count,
                        "percentage": round(percentage, 1)
                    })
                
                return MatchAnalytics(
                    match_id=match_id,
                    total_reactions=total_reactions,
                    emoji_breakdown=emoji_breakdown,
                    reactions_per_minute=reactions_per_minute,
                    top_emojis=top_emojis
                )
                
        except Exception as e:
            self.logger.error(f"Error getting match analytics for {match_id}: {e}")
            return None
    
    # PUBLIC_INTERFACE
    def get_global_analytics(self) -> GlobalAnalytics:
        """
        Get global analytics data
        
        Returns:
            Global analytics
        """
        try:
            with DatabaseSession() as db:
                # Total reactions
                total_reactions = db.query(func.count(Reaction.id)).scalar() or 0
                
                # Total unique users (approximate by session IDs)
                total_users = db.query(func.count(func.distinct(Reaction.user_session_id))).scalar() or 0
                
                # Active matches (live status)
                active_matches = db.query(func.count(Match.id)).filter(Match.status == "live").scalar() or 0
                
                # Top matches by reaction count
                top_matches_query = db.query(
                    Match.id,
                    Match.home_team_id,
                    Match.away_team_id,
                    Match.status,
                    func.count(Reaction.id).label('reaction_count')
                ).outerjoin(
                    Reaction, Reaction.match_id == Match.id
                ).group_by(
                    Match.id, Match.home_team_id, Match.away_team_id, Match.status
                ).order_by(
                    desc('reaction_count')
                ).limit(3).all()
                
                top_matches = []
                for match_id, home_team_id, away_team_id, status, reaction_count in top_matches_query:
                    home_team = db.query(Team).filter(Team.id == home_team_id).first()
                    away_team = db.query(Team).filter(Team.id == away_team_id).first()
                    
                    # Convert match_id to int for compatibility
                    matches = db.query(Match).all()
                    display_id = 1
                    for i, m in enumerate(matches):
                        if m.id == match_id:
                            display_id = i + 1
                            break
                    
                    top_matches.append({
                        "match_id": display_id,
                        "home_team": home_team.name if home_team else "Unknown",
                        "away_team": away_team.name if away_team else "Unknown", 
                        "total_reactions": reaction_count,
                        "status": "live" if status == "live" else "completed" if status == "completed" else "upcoming"
                    })
                
                # Emoji distribution
                emoji_distribution = {}
                emoji_counts = db.query(
                    Emoji.unicode_symbol,
                    func.count(Reaction.id)
                ).join(
                    Reaction, Reaction.emoji_id == Emoji.id
                ).group_by(
                    Emoji.unicode_symbol
                ).all()
                
                for emoji_symbol, count in emoji_counts:
                    emoji_distribution[emoji_symbol] = count
                
                # Reactions in last hour
                one_hour_ago = datetime.now() - timedelta(hours=1)
                reactions_last_hour = db.query(func.count(Reaction.id)).filter(
                    Reaction.reaction_timestamp >= one_hour_ago
                ).scalar() or 0
                
                return GlobalAnalytics(
                    total_users=total_users,
                    total_reactions=total_reactions,
                    active_matches=active_matches,
                    top_matches=top_matches,
                    emoji_distribution=emoji_distribution,
                    reactions_last_hour=reactions_last_hour,
                    peak_activity_time="15:30 - 16:00"  # Mock data for now
                )
                
        except Exception as e:
            self.logger.error(f"Error getting global analytics: {e}")
            return GlobalAnalytics(
                total_users=0,
                total_reactions=0,
                active_matches=0,
                top_matches=[],
                emoji_distribution={},
                reactions_last_hour=0,
                peak_activity_time="N/A"
            )
    
    def _convert_match_to_schema(self, match: Match) -> MatchSchema:
        """Convert database match model to schema"""
        try:
            # Generate a simple ID based on the match's position
            # This is a simplified approach for compatibility
            display_id = hash(str(match.id)) % 1000 + 1
            
            # Convert status
            status_map = {
                "live": MatchStatus.LIVE,
                "scheduled": MatchStatus.UPCOMING,
                "completed": MatchStatus.COMPLETED
            }
            
            # Get team information
            home_team_id = hash(str(match.home_team.id)) % 100 + 1
            away_team_id = hash(str(match.away_team.id)) % 100 + 1
            
            return MatchSchema(
                id=display_id,
                home_team=TeamSchema(
                    id=home_team_id,
                    name=match.home_team.name,
                    short_name=match.home_team.short_name,
                    logo_url=match.home_team.logo_url or "/images/default-logo.png",
                    primary_color=match.home_team.primary_color
                ),
                away_team=TeamSchema(
                    id=away_team_id,
                    name=match.away_team.name,
                    short_name=match.away_team.short_name,
                    logo_url=match.away_team.logo_url or "/images/default-logo.png",
                    primary_color=match.away_team.primary_color
                ),
                status=status_map.get(match.status, MatchStatus.UPCOMING),
                start_time=match.match_date,
                league=match.competition,
                score={"home": match.home_score, "away": match.away_score} if match.status in ["live", "completed"] else None,
                match_time="LIVE" if match.status == "live" else "FT" if match.status == "completed" else None,
                venue=match.venue or "TBD"
            )
        except Exception as e:
            self.logger.error(f"Error converting match to schema: {e}")
            # Return a fallback match
            return MatchSchema(
                id=1,
                home_team=TeamSchema(id=1, name="Team A", short_name="TEA", logo_url="/images/default.png", primary_color="#000000"),
                away_team=TeamSchema(id=2, name="Team B", short_name="TEB", logo_url="/images/default.png", primary_color="#000000"),
                status=MatchStatus.UPCOMING,
                start_time=datetime.now(),
                league="Unknown",
                score=None,
                match_time=None,
                venue="TBD"
            )


# Global database service instance  
database_service = DatabaseService()
