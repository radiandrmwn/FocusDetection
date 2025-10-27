"""
Data Manager Service
Handles persistence and retrieval of session history and statistics
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import logging
from models.session import Session, SessionType

logger = logging.getLogger(__name__)


class DataManager:
    """
    Manages session data persistence and analytics
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize data manager

        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "focus_history.json"
        self.sessions: List[Session] = []
        self.load_history()

    def load_history(self):
        """Load session history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session_list = data.get('sessions', [])
                    self.sessions = [Session.from_dict(s) for s in session_list]
                    logger.info(f"Loaded {len(self.sessions)} sessions from history")
            else:
                logger.info("No history file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            self.sessions = []

    def save_history(self):
        """Save session history to file"""
        try:
            data = {
                'sessions': [s.to_dict() for s in self.sessions],
                'last_updated': datetime.now().isoformat(),
                'total_sessions': len(self.sessions)
            }

            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.sessions)} sessions to history")
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def add_session(self, session: Session):
        """Add a completed session to history"""
        if session.statistics:
            self.sessions.append(session)
            self.save_history()
            logger.info(f"Session added: {session.session_type.value}")

    def get_sessions_by_date(self, date: datetime) -> List[Session]:
        """Get all sessions for a specific date"""
        target_date = date.date()
        return [
            s for s in self.sessions
            if s.start_time and s.start_time.date() == target_date
        ]

    def get_sessions_in_range(self, start_date: datetime,
                              end_date: datetime) -> List[Session]:
        """Get sessions within a date range"""
        return [
            s for s in self.sessions
            if s.start_time and start_date.date() <= s.start_time.date() <= end_date.date()
        ]

    def get_today_sessions(self) -> List[Session]:
        """Get today's sessions"""
        return self.get_sessions_by_date(datetime.now())

    def get_this_week_sessions(self) -> List[Session]:
        """Get this week's sessions"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        return self.get_sessions_in_range(week_start, today)

    def get_statistics_summary(self, sessions: List[Session] = None) -> Dict:
        """
        Get statistical summary for given sessions

        Args:
            sessions: List of sessions to analyze (defaults to all sessions)

        Returns:
            Dictionary with statistical summary
        """
        if sessions is None:
            sessions = self.sessions

        work_sessions = [s for s in sessions if s.session_type == SessionType.WORK]

        if not work_sessions:
            return {
                'total_sessions': 0,
                'total_focus_time': 0,
                'total_away_time': 0,
                'average_focus_score': 0,
                'total_distractions': 0,
                'best_session_score': 0,
                'worst_session_score': 0
            }

        total_focus_time = sum(s.statistics.focus_time for s in work_sessions)
        total_away_time = sum(s.statistics.away_time for s in work_sessions)
        total_distractions = sum(s.statistics.distraction_count for s in work_sessions)
        focus_scores = [s.statistics.focus_score for s in work_sessions]

        return {
            'total_sessions': len(work_sessions),
            'total_focus_time': total_focus_time,  # seconds
            'total_away_time': total_away_time,  # seconds
            'average_focus_score': sum(focus_scores) / len(focus_scores),
            'total_distractions': total_distractions,
            'best_session_score': max(focus_scores) if focus_scores else 0,
            'worst_session_score': min(focus_scores) if focus_scores else 0,
            'focus_time_hours': total_focus_time / 3600,
            'focus_time_minutes': total_focus_time / 60
        }

    def get_daily_statistics(self, days: int = 7) -> List[Dict]:
        """
        Get daily statistics for the last N days

        Args:
            days: Number of days to analyze

        Returns:
            List of daily statistics
        """
        daily_stats = []
        today = datetime.now()

        for i in range(days):
            date = today - timedelta(days=i)
            sessions = self.get_sessions_by_date(date)
            stats = self.get_statistics_summary(sessions)
            stats['date'] = date.strftime('%Y-%m-%d')
            stats['day_name'] = date.strftime('%A')
            daily_stats.append(stats)

        return list(reversed(daily_stats))

    def get_productivity_trends(self) -> Dict:
        """Get productivity trends and insights"""
        week_sessions = self.get_this_week_sessions()
        today_sessions = self.get_today_sessions()

        week_stats = self.get_statistics_summary(week_sessions)
        today_stats = self.get_statistics_summary(today_sessions)

        # Calculate trends
        daily_avg_sessions = week_stats['total_sessions'] / 7
        daily_avg_focus_minutes = week_stats['focus_time_minutes'] / 7

        return {
            'week_summary': week_stats,
            'today_summary': today_stats,
            'daily_average_sessions': daily_avg_sessions,
            'daily_average_focus_minutes': daily_avg_focus_minutes,
            'today_vs_average': (
                today_stats['total_sessions'] - daily_avg_sessions
                if daily_avg_sessions > 0 else 0
            )
        }

    def export_to_csv(self, filepath: str, sessions: List[Session] = None):
        """Export sessions to CSV format"""
        import csv

        if sessions is None:
            sessions = self.sessions

        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Date', 'Type', 'Duration (min)', 'Focus Time (min)',
                    'Away Time (min)', 'Focus Score', 'Distractions'
                ])

                for session in sessions:
                    if session.statistics:
                        writer.writerow([
                            session.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                            session.session_type.value,
                            session.planned_duration // 60,
                            session.statistics.focus_time // 60,
                            session.statistics.away_time // 60,
                            session.statistics.focus_score,
                            session.statistics.distraction_count
                        ])

            logger.info(f"Exported {len(sessions)} sessions to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    def clear_old_sessions(self, days_to_keep: int = 30):
        """Remove sessions older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        original_count = len(self.sessions)

        self.sessions = [
            s for s in self.sessions
            if s.start_time and s.start_time >= cutoff_date
        ]

        removed_count = original_count - len(self.sessions)
        if removed_count > 0:
            self.save_history()
            logger.info(f"Removed {removed_count} old sessions")

        return removed_count
