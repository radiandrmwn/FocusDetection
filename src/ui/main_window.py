"""
Main Window
Modern UI for Smart Focus Timer application
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QGridLayout, QSpinBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
import logging

from models.timer import PomodoroTimer
from models.session import SessionType, SessionState
from services.camera_service import CameraService
from services.data_manager import DataManager
from services.face_detector import FaceDetectionResult
from utils.config import get_config
from ui.styles.themes import get_theme, get_stylesheet, ThemeMode
from ui.widgets.stat_card import StatCard
from ui.widgets.timer_display import TimerDisplay
from ui.compact_window import CompactWindow

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Modern main window for Smart Focus Timer
    """

    def __init__(self):
        super().__init__()

        # Initialize configuration
        self.config = get_config()

        # Initialize theme
        theme_mode = ThemeMode(self.config.get('ui.theme', 'dark'))
        self.theme = get_theme(theme_mode)
        self.stylesheet = get_stylesheet(self.theme)

        # Initialize services and models
        timer_config = self.config.get_section('timer')
        self.timer = PomodoroTimer(
            work_duration=timer_config['work_duration'],
            short_break_duration=timer_config['short_break_duration'],
            long_break_duration=timer_config['long_break_duration'],
            daily_goal=timer_config['daily_goal']
        )

        self.data_manager = DataManager()
        self.camera_service = None

        # State
        self.current_face_status: FaceDetectionResult = None
        self.away_frames = 0

        # Compact window
        self.compact_window = None
        self.current_camera_pixmap = None  # Store current camera frame

        # Setup timer callbacks
        self.timer.on_session_complete = self.on_session_complete
        self.timer.on_state_change = self.on_state_change

        # Initialize UI
        self.init_ui()
        self.apply_theme()
        self.init_camera()

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)

        logger.info("Main window initialized")

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Smart Focus Timer - AI-Powered Productivity")

        # Get window size from config - increased default height to prevent cutoff
        width = self.config.get('ui.window_width', 1400)
        height = self.config.get('ui.window_height', 900)
        self.setGeometry(100, 100, width, height)
        self.setMinimumSize(1200, 850)  # Set minimum size to prevent shrinking

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_widget.setLayout(main_layout)

        # Left panel - Timer and controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)

        # Right panel - Camera and presence
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)

    def create_left_panel(self) -> QWidget:
        """Create left panel with timer and controls"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        panel.setLayout(layout)

        # Timer display
        self.timer_display = TimerDisplay()
        layout.addWidget(self.timer_display)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.start_btn.clicked.connect(self.start_timer)
        self.start_btn.setStyleSheet(self.stylesheet.get_button_style('success'))
        button_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.pause_btn.clicked.connect(self.pause_timer)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet(self.stylesheet.get_button_style('warning'))
        button_layout.addWidget(self.pause_btn)

        self.reset_btn = QPushButton("⟲ Reset")
        self.reset_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setStyleSheet(self.stylesheet.get_button_style('error'))
        button_layout.addWidget(self.reset_btn)

        layout.addLayout(button_layout)

        # Compact mode button (separate row)
        compact_btn_layout = QHBoxLayout()
        self.compact_btn = QPushButton("Compact Mode")
        self.compact_btn.setFont(QFont("Segoe UI", 12))
        self.compact_btn.clicked.connect(self.toggle_compact_mode)
        self.compact_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.colors['bg_elevated']};
                color: {self.theme.colors['text_primary']};
                border: 2px solid {self.theme.colors['primary']};
                border-radius: 10px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {self.theme.colors['primary']};
                color: #000000;
            }}
        """)
        compact_btn_layout.addWidget(self.compact_btn)
        layout.addLayout(compact_btn_layout)

        # Daily goal
        goal_group = QGroupBox("Daily Goal")
        goal_layout = QVBoxLayout()
        goal_layout.setSpacing(8)
        goal_layout.setContentsMargins(10, 15, 10, 10)

        self.goal_label = QLabel("0 / 8 sessions completed")
        self.goal_label.setAlignment(Qt.AlignCenter)
        self.goal_label.setFont(QFont("Segoe UI", 12))
        goal_layout.addWidget(self.goal_label)

        # Goal settings
        goal_settings_layout = QHBoxLayout()
        goal_settings_layout.addWidget(QLabel("Daily Target:"))
        self.goal_spinbox = QSpinBox()
        self.goal_spinbox.setMinimum(1)
        self.goal_spinbox.setMaximum(20)
        self.goal_spinbox.setValue(self.timer.daily_goal.target_sessions)
        self.goal_spinbox.setSuffix(" sessions")
        self.goal_spinbox.setButtonSymbols(QSpinBox.PlusMinus)
        self.goal_spinbox.valueChanged.connect(self.update_goal)
        goal_settings_layout.addWidget(self.goal_spinbox)
        goal_settings_layout.addStretch()
        goal_layout.addLayout(goal_settings_layout)

        goal_group.setLayout(goal_layout)
        layout.addWidget(goal_group)

        # Timer settings
        settings_group = QGroupBox("Timer Settings")
        settings_layout = QGridLayout()
        settings_layout.setSpacing(8)
        settings_layout.setContentsMargins(10, 15, 10, 10)

        settings_layout.addWidget(QLabel("Work:"), 0, 0)
        self.work_spinbox = QSpinBox()
        self.work_spinbox.setMinimum(1)
        self.work_spinbox.setMaximum(60)
        self.work_spinbox.setValue(self.timer.work_duration // 60)
        self.work_spinbox.setSuffix(" min")
        self.work_spinbox.setButtonSymbols(QSpinBox.PlusMinus)
        self.work_spinbox.valueChanged.connect(self.update_timer_settings)
        settings_layout.addWidget(self.work_spinbox, 0, 1)

        settings_layout.addWidget(QLabel("Short Break:"), 1, 0)
        self.break_spinbox = QSpinBox()
        self.break_spinbox.setMinimum(1)
        self.break_spinbox.setMaximum(30)
        self.break_spinbox.setValue(self.timer.short_break_duration // 60)
        self.break_spinbox.setSuffix(" min")
        self.break_spinbox.setButtonSymbols(QSpinBox.PlusMinus)
        self.break_spinbox.valueChanged.connect(self.update_timer_settings)
        settings_layout.addWidget(self.break_spinbox, 1, 1)

        settings_layout.addWidget(QLabel("Long Break:"), 2, 0)
        self.long_break_spinbox = QSpinBox()
        self.long_break_spinbox.setMinimum(5)
        self.long_break_spinbox.setMaximum(60)
        self.long_break_spinbox.setValue(self.timer.long_break_duration // 60)
        self.long_break_spinbox.setSuffix(" min")
        self.long_break_spinbox.setButtonSymbols(QSpinBox.PlusMinus)
        self.long_break_spinbox.valueChanged.connect(self.update_timer_settings)
        settings_layout.addWidget(self.long_break_spinbox, 2, 1)

        self.settings_info = QLabel("⚠ Cannot change while timer is running")
        self.settings_info.setStyleSheet("color: #f59e0b; font-size: 11px;")
        self.settings_info.setVisible(False)
        settings_layout.addWidget(self.settings_info, 3, 0, 1, 2)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        layout.addStretch()

        return panel

    def create_right_panel(self) -> QWidget:
        """Create right panel with camera feed"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        panel.setLayout(layout)

        # Header
        header = QLabel("Face Detection Monitor")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(header)

        # Camera feed
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(640, 480)
        self.camera_label.setStyleSheet(f"""
            border: 3px solid {self.theme.colors['border']};
            border-radius: 12px;
            background-color: {self.theme.colors['bg_tertiary']};
        """)
        self.camera_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.camera_label)

        # Presence indicator
        presence_group = QGroupBox("Presence Status")
        presence_layout = QVBoxLayout()
        presence_layout.setSpacing(10)

        self.presence_indicator = QLabel("● AWAY")
        self.presence_indicator.setAlignment(Qt.AlignCenter)
        self.presence_indicator.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.presence_indicator.setStyleSheet(f"""
            padding: 20px;
            background-color: {self.theme.colors['error']};
            color: white;
            border-radius: 12px;
        """)
        presence_layout.addWidget(self.presence_indicator)

        self.attention_indicator = QLabel("👁 Not Detected")
        self.attention_indicator.setAlignment(Qt.AlignCenter)
        self.attention_indicator.setFont(QFont("Segoe UI", 14))
        self.attention_indicator.setStyleSheet(f"color: {self.theme.colors['text_secondary']};")
        presence_layout.addWidget(self.attention_indicator)

        info_label = QLabel(
            "✓ Face detected = Timer runs\n"
            "✗ No face = Timer pauses\n"
            "👁 Eyes detected = Focused"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet(f"padding: 10px; color: {self.theme.colors['text_tertiary']};")
        presence_layout.addWidget(info_label)

        presence_group.setLayout(presence_layout)
        layout.addWidget(presence_group)

        layout.addStretch()

        return panel

    def apply_theme(self):
        """Apply theme to the application"""
        self.setStyleSheet(self.stylesheet.get_main_stylesheet())

    def init_camera(self):
        """Initialize camera service"""
        camera_index = self.config.get('camera.camera_index', 0)
        self.camera_service = CameraService(camera_index=camera_index)
        self.camera_service.frame_ready.connect(self.update_camera_feed)
        self.camera_service.face_status.connect(self.update_face_status)
        self.camera_service.error_occurred.connect(self.handle_camera_error)
        self.camera_service.start()
        logger.info("Camera service started")

    def update_camera_feed(self, frame: np.ndarray):
        """Update camera feed display"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)

            # Store for compact window
            self.current_camera_pixmap = pixmap

            # Update main window camera feed
            scaled_pixmap = pixmap.scaled(
                self.camera_label.width(),
                self.camera_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.camera_label.setPixmap(scaled_pixmap)

            # Update compact window if it exists
            if self.compact_window and self.compact_window.isVisible():
                self.compact_window.update_camera_frame(pixmap)
        except Exception as e:
            logger.error(f"Error updating camera feed: {e}")

    def update_face_status(self, result: FaceDetectionResult):
        """Update face detection status"""
        self.current_face_status = result

        if result.face_detected:
            self.presence_indicator.setText("● PRESENT")
            self.presence_indicator.setStyleSheet(f"""
                padding: 20px;
                background-color: {self.theme.colors['success']};
                color: white;
                border-radius: 12px;
            """)
            self.away_frames = 0

            if result.focused:
                self.attention_indicator.setText("👁 FOCUSED")
                self.attention_indicator.setStyleSheet(f"color: {self.theme.colors['success']};")
            else:
                self.attention_indicator.setText("👁 Present")
                self.attention_indicator.setStyleSheet(f"color: {self.theme.colors['warning']};")
        else:
            self.presence_indicator.setText("● AWAY")
            self.presence_indicator.setStyleSheet(f"""
                padding: 20px;
                background-color: {self.theme.colors['error']};
                color: white;
                border-radius: 12px;
            """)
            self.attention_indicator.setText("👁 Not Detected")
            self.attention_indicator.setStyleSheet(f"color: {self.theme.colors['error']};")

            # Count away frames for distraction tracking
            if self.timer.get_state() == SessionState.RUNNING:
                self.away_frames += 1
                if self.away_frames == 3:  # After 3 seconds
                    self.timer.distraction_count += 1

    def handle_camera_error(self, error_msg: str):
        """Handle camera errors"""
        logger.error(error_msg)
        self.camera_label.setText(f"Camera Error:\n{error_msg}")

    def start_timer(self):
        """Start timer"""
        if self.timer.get_state() == SessionState.NOT_STARTED:
            self.timer.start_work_session()

        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        logger.info("Timer started")

    def pause_timer(self):
        """Pause/resume timer"""
        state = self.timer.get_state()

        if state == SessionState.RUNNING:
            self.timer.pause(is_away=False)
            self.pause_btn.setText("▶ Resume")
        elif state in (SessionState.PAUSED, SessionState.PAUSED_AWAY):
            self.timer.resume()
            self.pause_btn.setText("⏸ Pause")

    def reset_timer(self):
        """Reset timer"""
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Pause")
        self.settings_info.setVisible(False)
        self.update_display()
        logger.info("Timer reset")

    def update_timer_settings(self):
        """Update timer durations"""
        success = self.timer.set_durations(
            self.work_spinbox.value(),
            self.break_spinbox.value(),
            self.long_break_spinbox.value()
        )

        if success:
            self.settings_info.setVisible(False)
            self.timer_display.set_time(self.timer.get_time_display())
        else:
            self.settings_info.setVisible(True)

    def update_goal(self):
        """Update daily goal"""
        self.timer.set_daily_goal(self.goal_spinbox.value())
        self.update_display()

    def update_display(self):
        """Update all display elements"""
        # Tick the timer
        if self.current_face_status:
            self.timer.tick(
                user_present=self.current_face_status.face_detected,
                user_focused=self.current_face_status.focused
            )

        # Update timer display
        self.timer_display.set_time(self.timer.get_time_display())
        self.timer_display.set_progress(self.timer.get_progress_percentage())

        # Update session type
        session_type = self.timer.get_session_type()
        if session_type == SessionType.WORK:
            self.timer_display.set_session_type("WORK SESSION", self.theme.colors['work'])
        elif session_type == SessionType.SHORT_BREAK:
            self.timer_display.set_session_type("SHORT BREAK", self.theme.colors['break'])
        elif session_type == SessionType.LONG_BREAK:
            self.timer_display.set_session_type("LONG BREAK", self.theme.colors['break'])
        else:
            self.timer_display.set_session_type("READY", self.theme.colors['primary'])

        # Update status
        self.update_status()

        # Update statistics
        # Update daily goal
        goal = self.timer.daily_goal
        self.goal_label.setText(f"{goal.completed_sessions} / {goal.target_sessions} sessions completed")

        # Update compact window if visible
        self.update_compact_window()

    def update_status(self):
        """Update status label"""
        state = self.timer.get_state()

        if state == SessionState.NOT_STARTED:
            self.timer_display.set_status("Ready to start your focus session")
        elif state == SessionState.PAUSED:
            self.timer_display.set_status("⏸ Paused (manual)")
        elif state == SessionState.PAUSED_AWAY:
            self.timer_display.set_status("⏸ Paused - You're away!")
        elif state == SessionState.RUNNING:
            if self.timer.get_session_type() == SessionType.WORK:
                if self.current_face_status and self.current_face_status.focused:
                    self.timer_display.set_status("✓ Working - Fully Focused!")
                else:
                    self.timer_display.set_status("✓ Working - Stay Focused")
            else:
                self.timer_display.set_status("☕ Break Time - Relax!")

    def on_session_complete(self, session):
        """Handle session completion"""
        self.data_manager.add_session(session)
        logger.info(f"Session completed and saved: {session.session_type.value}")
        # TODO: Add notification sound here

    def on_state_change(self, state: SessionState):
        """Handle state changes"""
        logger.info(f"Timer state changed to: {state.value}")
        self.update_display()

    def toggle_compact_mode(self):
        """Toggle between full and compact mode"""
        if self.compact_window is None or not self.compact_window.isVisible():
            # Create and show compact window
            self.compact_window = CompactWindow(self.theme, self)

            # Connect expand button to restore full view
            self.compact_window.expand_btn.clicked.connect(self.restore_full_view)

            # Position compact window (top-right of screen)
            screen_geometry = self.screen().availableGeometry()
            x = screen_geometry.width() - self.compact_window.width() - 20
            y = 20
            self.compact_window.move(x, y)

            # Update compact window with current state
            self.update_compact_window()

            # Show compact window and hide main window
            self.compact_window.show()
            self.hide()

            logger.info("Switched to compact mode")
        else:
            # Already in compact mode, restore full view
            self.restore_full_view()

    def restore_full_view(self):
        """Restore to full window view"""
        if self.compact_window and self.compact_window.isVisible():
            self.compact_window.hide()
        self.show()
        self.activateWindow()
        logger.info("Restored to full view")

    def update_compact_window(self):
        """Update compact window with current timer data"""
        if not self.compact_window or not self.compact_window.isVisible():
            return

        # Update timer
        self.compact_window.set_time(self.timer.get_time_display())
        self.compact_window.set_progress(self.timer.get_progress_percentage())

        # Update session type
        session_type = self.timer.get_session_type()
        if session_type == SessionType.WORK:
            self.compact_window.set_session_type("WORK", self.theme.colors['work'])
        elif session_type == SessionType.SHORT_BREAK:
            self.compact_window.set_session_type("BREAK", self.theme.colors['break'])
        elif session_type == SessionType.LONG_BREAK:
            self.compact_window.set_session_type("LONG BREAK", self.theme.colors['break'])
        else:
            self.compact_window.set_session_type("READY", self.theme.colors['primary'])

        # Update presence
        if self.current_face_status:
            self.compact_window.set_presence(
                self.current_face_status.face_detected,
                self.current_face_status.focused
            )

        # Update status
        state = self.timer.get_state()
        if state == SessionState.NOT_STARTED:
            self.compact_window.set_status("Ready")
        elif state == SessionState.PAUSED:
            self.compact_window.set_status("⏸ Paused")
        elif state == SessionState.PAUSED_AWAY:
            self.compact_window.set_status("Away")
        elif state == SessionState.RUNNING:
            if self.timer.get_session_type() == SessionType.WORK:
                self.compact_window.set_status("Working")
            else:
                self.compact_window.set_status("Break")

        # Update camera if available
        if self.current_camera_pixmap:
            self.compact_window.update_camera_frame(self.current_camera_pixmap)

    def closeEvent(self, event):
        """Handle window close"""
        logger.info("Application closing...")
        if self.compact_window:
            self.compact_window.close()
        if self.camera_service:
            self.camera_service.stop()
        self.data_manager.save_history()
        event.accept()
