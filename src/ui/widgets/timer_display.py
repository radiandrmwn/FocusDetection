"""
Timer Display Widget
Large, beautiful timer display with animations
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont


class TimerDisplay(QWidget):
    """
    Beautiful animated timer display
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 5, 10, 5)

        # Session type label
        self.session_label = QLabel("READY")
        self.session_label.setAlignment(Qt.AlignCenter)
        self.session_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.session_label.setStyleSheet("""
            padding: 5px;
            border-radius: 6px;
            background-color: rgba(255, 255, 255, 0.15);
            color: #ffffff;
        """)
        layout.addWidget(self.session_label)

        # Time display
        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Segoe UI", 48, QFont.Bold))
        self.time_label.setStyleSheet("color: #ffffff; padding: 5px;")
        layout.addWidget(self.time_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ffffff;
                border-radius: 12px;
                text-align: center;
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 13px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: #ffffff;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready to start")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("color: #b0b0b0; padding: 5px;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # Animation for progress bar
        self.progress_animation = QPropertyAnimation(self, b"progress")
        self.progress_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.progress_animation.setDuration(300)

    def set_time(self, time_str: str):
        """Set the time display"""
        self.time_label.setText(time_str)

    def set_progress(self, percentage: int):
        """Set progress with animation"""
        self.progress_animation.stop()
        self.progress_animation.setStartValue(self._progress)
        self.progress_animation.setEndValue(percentage)
        self.progress_animation.start()

    def set_session_type(self, session_type: str, color: str = "#ffffff"):
        """Set session type label"""
        self.session_label.setText(session_type)
        self.session_label.setStyleSheet(f"""
            padding: 5px;
            border-radius: 6px;
            background-color: rgba(255, 255, 255, 0.15);
            color: {color};
            font-weight: bold;
        """)
        self.time_label.setStyleSheet(f"color: {color}; padding: 5px;")
        self._update_progress_bar_color(color)

    def set_status(self, status: str):
        """Set status label"""
        self.status_label.setText(status)

    def _update_progress_bar_color(self, color: str):
        """Update progress bar color"""
        # Use neutral white/gray colors
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {color};
                border-radius: 12px;
                text-align: center;
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                font-size: 13px;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 10px;
            }}
        """)

    @pyqtProperty(int)
    def progress(self):
        """Progress property getter"""
        return self._progress

    @progress.setter
    def progress(self, value):
        """Progress property setter"""
        self._progress = value
        self.progress_bar.setValue(value)
