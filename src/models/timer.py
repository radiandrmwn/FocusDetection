"""
Pomodoro Timer Model
Core business logic for the Pomodoro technique
"""

from typing import Optional, Callable
from datetime import datetime, timedelta
import logging
from .session import Session, SessionType, SessionState, SessionStatistics, DailyGoal

logger = logging.getLogger(__name__)


class PomodoroTimer:
    """
    Enhanced Pomodoro timer with better state management and callbacks
    """

    def __init__(self,
                 work_duration: int = 25,
                 short_break_duration: int = 5,
                 long_break_duration: int = 15,
                 sessions_until_long_break: int = 4,
                 daily_goal: int = 8):
        """
        Initialize Pomodoro timer

        Args:
            work_duration: Work session duration in minutes
            short_break_duration: Short break duration in minutes
            long_break_duration: Long break duration in minutes
            sessions_until_long_break: Number of work sessions before long break
            daily_goal: Target number of work sessions per day
        """
        # Duration settings (stored in seconds)
        self.work_duration = work_duration * 60
        self.short_break_duration = short_break_duration * 60
        self.long_break_duration = long_break_duration * 60
        self.sessions_until_long_break = sessions_until_long_break

        # Current session
        self.current_session: Optional[Session] = None
        self.time_remaining: int = self.work_duration
        self.session_count = 0  # Count for determining long break

        # Statistics
        self.total_focus_time = 0
        self.total_break_time = 0
        self.total_away_time = 0
        self.current_session_focus_time = 0
        self.current_session_away_time = 0
        self.distraction_count = 0

        # Daily goal
        self.daily_goal = DailyGoal(target_sessions=daily_goal)

        # Callbacks
        self.on_session_complete: Optional[Callable[[Session], None]] = None
        self.on_tick: Optional[Callable[[int], None]] = None
        self.on_state_change: Optional[Callable[[SessionState], None]] = None

    def start_work_session(self):
        """Start a new work session"""
        self.current_session = Session(
            session_type=SessionType.WORK,
            planned_duration=self.work_duration
        )
        self.current_session.start()
        self.time_remaining = self.work_duration
        self.current_session_focus_time = 0
        self.current_session_away_time = 0
        self.distraction_count = 0

        logger.info("Work session started")
        self._notify_state_change()

    def start_break_session(self):
        """Start a break session (short or long based on session count)"""
        # Determine break type
        is_long_break = (self.session_count % self.sessions_until_long_break == 0
                        and self.session_count > 0)

        session_type = SessionType.LONG_BREAK if is_long_break else SessionType.SHORT_BREAK
        duration = self.long_break_duration if is_long_break else self.short_break_duration

        self.current_session = Session(
            session_type=session_type,
            planned_duration=duration
        )
        self.current_session.start()
        self.time_remaining = duration

        logger.info(f"Break session started: {session_type.value}")
        self._notify_state_change()

    def pause(self, is_away: bool = False):
        """Pause the current session"""
        if self.current_session and self.current_session.state == SessionState.RUNNING:
            self.current_session.pause(is_away)
            logger.info(f"Session paused (away: {is_away})")
            self._notify_state_change()

    def resume(self):
        """Resume the current session"""
        if self.current_session and self.current_session.state in (
            SessionState.PAUSED, SessionState.PAUSED_AWAY
        ):
            self.current_session.resume()
            logger.info("Session resumed")
            self._notify_state_change()

    def stop(self):
        """Stop and reset the current session"""
        if self.current_session:
            self.current_session = None
            self.time_remaining = self.work_duration
            logger.info("Session stopped")
            self._notify_state_change()

    def tick(self, user_present: bool = True, user_focused: bool = False):
        """
        Process one second tick

        Args:
            user_present: Whether user's face is detected
            user_focused: Whether user is actively looking at screen
        """
        if not self.current_session or self.current_session.state != SessionState.RUNNING:
            return

        # Handle work session
        if self.current_session.session_type == SessionType.WORK:
            if user_present:
                # User is present, count time
                self.time_remaining -= 1
                self.total_focus_time += 1
                self.current_session_focus_time += 1

                # Track focus quality
                if user_focused:
                    # Bonus: user is actively focused
                    pass
            else:
                # User is away, pause timer and count away time
                self.total_away_time += 1
                self.current_session_away_time += 1

        # Handle break session (always counts down regardless of presence)
        else:
            self.time_remaining -= 1
            self.total_break_time += 1

        # Check if session is complete
        if self.time_remaining <= 0:
            self._complete_current_session()

        # Notify tick
        if self.on_tick:
            self.on_tick(self.time_remaining)

    def _complete_current_session(self):
        """Complete the current session and start next one"""
        if not self.current_session:
            return

        # Calculate statistics
        total_time = self.current_session_focus_time + self.current_session_away_time
        focus_percentage = (
            (self.current_session_focus_time / total_time * 100)
            if total_time > 0 else 100
        )

        statistics = SessionStatistics(
            total_duration=self.current_session.planned_duration,
            focus_time=self.current_session_focus_time,
            away_time=self.current_session_away_time,
            distraction_count=self.distraction_count,
            focus_percentage=focus_percentage
        )

        self.current_session.complete(statistics)

        # Notify completion
        if self.on_session_complete:
            self.on_session_complete(self.current_session)

        logger.info(f"Session completed: {self.current_session.session_type.value}, "
                   f"Focus: {statistics.focus_score}%")

        # Update counters
        if self.current_session.session_type == SessionType.WORK:
            self.session_count += 1
            self.daily_goal.reset_if_new_day()
            self.daily_goal.increment()
            # Start break
            self.start_break_session()
        else:
            # Start new work session
            self.start_work_session()

    def set_durations(self, work_minutes: int, short_break_minutes: int,
                     long_break_minutes: int = None):
        """Update session durations (only when not running)"""
        if self.current_session and self.current_session.state == SessionState.RUNNING:
            logger.warning("Cannot change durations while session is running")
            return False

        self.work_duration = work_minutes * 60
        self.short_break_duration = short_break_minutes * 60

        if long_break_minutes:
            self.long_break_duration = long_break_minutes * 60

        # Update current time remaining if needed
        if not self.current_session:
            self.time_remaining = self.work_duration

        logger.info(f"Durations updated: work={work_minutes}m, "
                   f"short_break={short_break_minutes}m, "
                   f"long_break={long_break_minutes}m")
        return True

    def set_daily_goal(self, goal: int):
        """Set daily goal target"""
        self.daily_goal.target_sessions = goal
        logger.info(f"Daily goal set to {goal} sessions")

    def get_time_display(self) -> str:
        """Get formatted time string (MM:SS)"""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_progress_percentage(self) -> int:
        """Get current session progress as percentage"""
        if not self.current_session:
            return 0

        total = self.current_session.planned_duration
        elapsed = total - self.time_remaining
        return int((elapsed / total) * 100) if total > 0 else 0

    def get_state(self) -> SessionState:
        """Get current session state"""
        return self.current_session.state if self.current_session else SessionState.NOT_STARTED

    def get_session_type(self) -> Optional[SessionType]:
        """Get current session type"""
        return self.current_session.session_type if self.current_session else None

    def get_focus_score(self) -> int:
        """Calculate overall focus score (0-100)"""
        total_work_time = self.total_focus_time + self.total_away_time
        if total_work_time == 0:
            return 100

        focus_percentage = (self.total_focus_time / total_work_time) * 100
        return min(100, int(focus_percentage))

    def _notify_state_change(self):
        """Notify state change callback"""
        if self.on_state_change and self.current_session:
            self.on_state_change(self.current_session.state)
