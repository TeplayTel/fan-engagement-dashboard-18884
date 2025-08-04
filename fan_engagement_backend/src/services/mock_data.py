from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random
from src.models.schemas import (
    Match, Team, MatchStatus, EmojiType, MatchAnalytics, 
    GlobalAnalytics, EmojiReaction, EmojiReactionResponse
)

class MockDataService:
    """Service to provide mock data for matches, teams, and analytics"""
    
    def __init__(self):
        self.teams = self._create_mock_teams()
        self.matches = self._create_mock_matches()
        self.reactions = []  # Store reactions in memory
        self.analytics_data = self._initialize_analytics()
    
    def _create_mock_teams(self) -> List[Team]:
        """Create mock team data"""
        return [
            Team(id=1, name="Arsenal", short_name="ARS", logo_url="/images/arsenal.png", primary_color="#DC143C"),
            Team(id=2, name="Chelsea", short_name="CHE", logo_url="/images/chelsea.png", primary_color="#034694"),
            Team(id=3, name="Manchester United", short_name="MUN", logo_url="/images/manchester_united.png", primary_color="#DA020E"),
            Team(id=4, name="Liverpool", short_name="LIV", logo_url="/images/liverpool.png", primary_color="#C8102E"),
            Team(id=5, name="Manchester City", short_name="MCI", logo_url="/images/manchester_city.png", primary_color="#6CABDD"),
            Team(id=6, name="Tottenham", short_name="TOT", logo_url="/images/tottenham.png", primary_color="#132257"),
            Team(id=7, name="Newcastle", short_name="NEW", logo_url="/images/newcastle.png", primary_color="#241F20"),
            Team(id=8, name="Brighton", short_name="BRI", logo_url="/images/brighton.png", primary_color="#0057B7"),
        ]
    
    def _create_mock_matches(self) -> List[Match]:
        """Create mock match data"""
        now = datetime.now()
        matches = []
        
        # Live match
        matches.append(Match(
            id=1,
            home_team=self.teams[0],  # Arsenal
            away_team=self.teams[1],  # Chelsea
            status=MatchStatus.LIVE,
            start_time=now - timedelta(hours=1),
            league="Premier League",
            score={"home": 2, "away": 1},
            match_time="78'",
            venue="Emirates Stadium"
        ))
        
        # Upcoming matches
        matches.append(Match(
            id=2,
            home_team=self.teams[2],  # Manchester United
            away_team=self.teams[3],  # Liverpool
            status=MatchStatus.UPCOMING,
            start_time=now + timedelta(hours=2),
            league="Premier League",
            score=None,
            match_time=None,
            venue="Old Trafford"
        ))
        
        matches.append(Match(
            id=3,
            home_team=self.teams[4],  # Manchester City
            away_team=self.teams[5],  # Tottenham
            status=MatchStatus.UPCOMING,
            start_time=now + timedelta(days=1),
            league="Premier League",
            score=None,
            match_time=None,
            venue="Etihad Stadium"
        ))
        
        # Completed matches
        matches.append(Match(
            id=4,
            home_team=self.teams[6],  # Newcastle
            away_team=self.teams[7],  # Brighton
            status=MatchStatus.COMPLETED,
            start_time=now - timedelta(days=1),
            league="Premier League",
            score={"home": 3, "away": 0},
            match_time="FT",
            venue="St. James' Park"
        ))
        
        matches.append(Match(
            id=5,
            home_team=self.teams[1],  # Chelsea
            away_team=self.teams[4],  # Manchester City
            status=MatchStatus.COMPLETED,
            start_time=now - timedelta(days=2),
            league="Premier League",
            score={"home": 1, "away": 2},
            match_time="FT",
            venue="Stamford Bridge"
        ))
        
        return matches
    
    def _initialize_analytics(self) -> Dict[str, Any]:
        """Initialize analytics data"""
        return {
            "total_reactions": 0,
            "emoji_counts": {emoji.value: 0 for emoji in EmojiType},
            "match_analytics": {match.id: {
                "total_reactions": random.randint(50, 500),
                "emoji_breakdown": {emoji.value: random.randint(5, 50) for emoji in EmojiType}
            } for match in self.matches}
        }
    
    def get_matches(self, filters: Optional[Dict[str, Any]] = None) -> List[Match]:
        """Get matches with optional filtering"""
        matches = self.matches.copy()
        
        if not filters:
            return matches
        
        if filters.get("status"):
            matches = [m for m in matches if m.status == filters["status"]]
        
        if filters.get("league"):
            matches = [m for m in matches if m.league.lower() == filters["league"].lower()]
        
        if filters.get("team"):
            team_filter = filters["team"].lower()
            matches = [m for m in matches if 
                      team_filter in m.home_team.name.lower() or 
                      team_filter in m.away_team.name.lower()]
        
        if filters.get("date_from"):
            matches = [m for m in matches if m.start_time >= filters["date_from"]]
        
        if filters.get("date_to"):
            matches = [m for m in matches if m.start_time <= filters["date_to"]]
        
        return matches
    
    def get_match_by_id(self, match_id: int) -> Optional[Match]:
        """Get a specific match by ID"""
        return next((match for match in self.matches if match.id == match_id), None)
    
    def add_emoji_reaction(self, reaction: EmojiReaction) -> EmojiReactionResponse:
        """Add an emoji reaction and update analytics"""
        # Create response with timestamp
        reaction_response = EmojiReactionResponse(
            id=len(self.reactions) + 1,
            match_id=reaction.match_id,
            emoji_type=reaction.emoji_type,
            user_id=reaction.user_id,
            timestamp=datetime.now()
        )
        
        # Store the reaction
        self.reactions.append(reaction)
        
        # Update analytics
        self._update_analytics(reaction)
        
        return reaction_response
    
    def _update_analytics(self, reaction: EmojiReaction):
        """Update analytics when a new reaction is added"""
        self.analytics_data["total_reactions"] += 1
        self.analytics_data["emoji_counts"][reaction.emoji_type.value] += 1
        
        # Update match-specific analytics
        if reaction.match_id in self.analytics_data["match_analytics"]:
            match_analytics = self.analytics_data["match_analytics"][reaction.match_id]
            match_analytics["total_reactions"] += 1
            match_analytics["emoji_breakdown"][reaction.emoji_type.value] += 1
    
    def get_match_analytics(self, match_id: int) -> Optional[MatchAnalytics]:
        """Get analytics for a specific match"""
        if match_id not in self.analytics_data["match_analytics"]:
            return None
        
        match_data = self.analytics_data["match_analytics"][match_id]
        
        # Create reactions per minute data (mock)
        reactions_per_minute = []
        for minute in range(0, 90, 10):
            reactions_per_minute.append({
                "minute": minute,
                "count": random.randint(5, 25)
            })
        
        # Create top emojis list
        emoji_breakdown = match_data["emoji_breakdown"]
        total = sum(emoji_breakdown.values())
        top_emojis = []
        
        for emoji, count in sorted(emoji_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / total * 100) if total > 0 else 0
            top_emojis.append({
                "emoji": emoji,
                "count": count,
                "percentage": round(percentage, 1)
            })
        
        return MatchAnalytics(
            match_id=match_id,
            total_reactions=match_data["total_reactions"],
            emoji_breakdown=emoji_breakdown,
            reactions_per_minute=reactions_per_minute,
            top_emojis=top_emojis
        )
    
    def get_global_analytics(self) -> GlobalAnalytics:
        """Get global analytics data"""
        # Calculate top matches by reaction count
        top_matches = []
        for match in self.matches[:3]:  # Top 3 matches
            analytics = self.analytics_data["match_analytics"].get(match.id, {})
            total_reactions = analytics.get("total_reactions", 0)
            top_matches.append({
                "match_id": match.id,
                "home_team": match.home_team.name,
                "away_team": match.away_team.name,
                "total_reactions": total_reactions,
                "status": match.status.value
            })
        
        # Sort by reactions
        top_matches.sort(key=lambda x: x["total_reactions"], reverse=True)
        
        return GlobalAnalytics(
            total_users=random.randint(1500, 3000),
            total_reactions=self.analytics_data["total_reactions"],
            active_matches=len([m for m in self.matches if m.status == MatchStatus.LIVE]),
            top_matches=top_matches,
            emoji_distribution=self.analytics_data["emoji_counts"],
            reactions_last_hour=random.randint(200, 800),
            peak_activity_time="15:30 - 16:00"
        )

# Global instance
mock_data_service = MockDataService()
