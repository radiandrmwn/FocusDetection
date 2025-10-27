"""
Session Data Models
Represents work/break sessions and their statistics
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict
from enum import Enum


class SessionType(Enum):
    """Types of Pomodoro sessions"""
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class SessionState(Enum):
    """States of a session"""
    NOT_STARTED = "not_started"
    RUNNING = "running"
    PAUSED = "paused"
    PAUSED_AWAY = "paused_away"
    COMPLETED = "completed"


@dataclass
class SessionStatistics:
    """Statistics for a completed session"""
    total_duration: int  # seconds
    focus_time: int  # seconds actually focused
    away_time: int  # seconds away
    distraction_count: int
    focus_percentage: float

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @property
    def focus_score(self) -> int:
        """Calculate focus score (0-100)"""
        return min(100, int(self.focus_percentage))


@dataclass
class Session:
    """Represents a Pomodoro session"""
    session_type: SessionType
    planned_duration: int  # seconds
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    state: SessionState = SessionState.NOT_STARTED
    statistics: Optional[SessionStatistics] = None

    def start(self):
        """Start the session"""
        self.start_time = datetime.now()
        self.state = SessionState.RUNNING

    def pause(self, is_away: bool = False):
        """Pause the session"""
        self.state = SessionState.PAUSED_AWAY if is_away else SessionState.PAUSED

    def resume(self):
        """Resume the session"""
        self.state = SessionState.RUNNING

    def complete(self, statistics: SessionStatistics):
        """Complete the session"""
        self.end_time = datetime.now()
        self.state = SessionState.COMPLETED
        self.statistics = statistics

    def to_dict(self) -> Dict:
        """Convert session to dictionary for storage"""
        return {
            'session_type': self.session_type.value,
            'planned_duration': self.planned_duration,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'state': self.state.value,
            'statistics': self.statistics.to_dict() if self.statistics else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Session':
        """Create session from dictionary"""
        session = cls(
            session_type=SessionType(data['session_type']),
            planned_duration=data['planned_duration'],
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            state=SessionState(data['state'])
        )

        if data.get('statistics'):
            stats_data = data['statistics']
            session.statistics = SessionStatistics(**stats_data)

        return session


@dataclass
class DailyGoal:
    """Daily goal tracking"""
    target_sessions: int
    completed_sessions: int = 0
    date: datetime = None

    def __post_init__(self):
        if self.date is None:
            self.date = datetime.now().date()

    @property
    def progress_percentage(self) -> int:
        """Get progress as percentage"""
        if self.target_sessions == 0:
            return 100
        return min(100, int((self.completed_sessions / self.target_sessions) * 100))

    @property
    def is_complete(self) -> bool:
        """Check if goal is complete"""
        return self.completed_sessions >= self.target_sessions

    def increment(self):
        """Increment completed sessions"""
        self.completed_sessions += 1

    def reset_if_new_day(self):
        """Reset counter if it's a new day"""
        today = datetime.now().date()
        if self.date != today:
            self.completed_sessions = 0
            self.date = today
