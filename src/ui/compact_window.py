"""
Compact Window Mode
Minimized floating window showing timer and camera feed
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QCursor
import numpy as np


class CompactWindow(QWidget):
    """
    Compact floating window similar to Microsoft Teams mini view
    Shows timer and camera feed in a small draggable window
    """

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.dragging = False
        self.drag_position = QPoint()
        self.init_ui()

    def init_ui(self):
        """Initialize compact window UI"""
        # Window flags for floating behavior
        self.setWindowFlags(
            Qt.Window |
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )

        # Very small size - Microsoft Teams style
        self.setFixedSize(220, 260)

        # Main layout with minimal padding
        layout = QVBoxLayout()
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)
        self.setLayout(layout)

        # Header bar with timer and controls
        header = self.create_header()
        layout.addWidget(header)

        # Camera feed - smaller
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(208, 156)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet(f"""
            background-color: {self.theme.colors['bg_tertiary']};
            border: 1px solid {self.theme.colors['border']};
            border-radius: 6px;
        """)
        layout.addWidget(self.camera_label)

        # Apply styling
        self.apply_style()

    def create_header(self) -> QWidget:
        """Create header with timer and controls"""
        header = QWidget()
        header.setFixedHeight(90)
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(3, 3, 3, 3)
        header_layout.setSpacing(0)
        header.setLayout(header_layout)

        # Top row: Control buttons
        top_row = QHBoxLayout()
        top_row.addStretch()

        # Expand button
        self.expand_btn = QPushButton("□")
        self.expand_btn.setFixedSize(24, 24)
        self.expand_btn.setFont(QFont("Segoe UI", 10))
        self.expand_btn.setToolTip("Expand to full view")
        self.expand_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.colors['bg_elevated']};
                border: 1px solid {self.theme.colors['border']};
                border-radius: 12px;
                color: {self.theme.colors['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {self.theme.colors['primary']};
                color: #000000;
            }}
        """)
        top_row.addWidget(self.expand_btn)

        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setFont(QFont("Segoe UI", 14, QFont.Bold))
        close_btn.setToolTip("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.theme.colors['bg_elevated']};
                border: 1px solid {self.theme.colors['border']};
                border-radius: 12px;
                color: {self.theme.colors['text_primary']};
            }}
            QPushButton:hover {{
                background-color: {self.theme.colors['error']};
                color: #ffffff;
            }}
        """)
        top_row.addWidget(close_btn)

        header_layout.addLayout(top_row)

        # Timer display - smaller and more compact
        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        self.time_label.setStyleSheet(f"color: {self.theme.colors['text_primary']}; padding: 0px;")
        header_layout.addWidget(self.time_label)

        # Hidden labels for compatibility (will be kept but not displayed)
        self.session_label = QLabel()
        self.session_label.hide()
        self.progress_label = QLabel()
        self.progress_label.hide()
        self.presence_label = QLabel()
        self.presence_label.hide()
        self.status_label = QLabel()
        self.status_label.hide()

        return header

    def create_status_bar(self) -> QWidget:
        """Create status bar at bottom"""
        status_bar = QWidget()
        status_bar.setFixedHeight(70)
        status_layout = QVBoxLayout()
        status_layout.setContentsMargins(8, 5, 8, 8)
        status_layout.setSpacing(4)
        status_bar.setLayout(status_layout)

        # Presence indicator
        self.presence_label = QLabel("● AWAY")
        self.presence_label.setAlignment(Qt.AlignCenter)
        self.presence_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.presence_label.setStyleSheet(f"""
            padding: 6px 12px;
            background-color: {self.theme.colors['error']};
            color: white;
            border-radius: 8px;
        """)
        status_layout.addWidget(self.presence_label)

        # Status text
        self.status_label = QLabel("Ready to start")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 9))
        self.status_label.setStyleSheet(f"color: {self.theme.colors['text_tertiary']}; padding-top: 2px;")
        status_layout.addWidget(self.status_label)

        return status_bar

    def apply_style(self):
        """Apply window styling"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.theme.colors['bg_secondary']};
                border: 2px solid {self.theme.colors['primary']};
                border-radius: 12px;
            }}
        """)

    def set_time(self, time_str: str):
        """Update time display"""
        self.time_label.setText(time_str)

    def set_progress(self, percentage: int):
        """Update progress display"""
        self.progress_label.setText(f"{percentage}%")

    def set_session_type(self, session_type: str, color: str):
        """Update session type"""
        self.session_label.setText(session_type)
        self.session_label.setStyleSheet(f"color: {color};")
        self.time_label.setStyleSheet(f"color: {color};")

    def set_presence(self, present: bool, focused: bool):
        """Update presence indicator"""
        if present:
            if focused:
                self.presence_label.setText("● FOCUSED")
                self.presence_label.setStyleSheet(f"""
                    padding: 6px 12px;
                    background-color: {self.theme.colors['focus']};
                    color: white;
                    border-radius: 8px;
                """)
            else:
                self.presence_label.setText("● PRESENT")
                self.presence_label.setStyleSheet(f"""
                    padding: 6px 12px;
                    background-color: {self.theme.colors['success']};
                    color: white;
                    border-radius: 8px;
                """)
        else:
            self.presence_label.setText("● AWAY")
            self.presence_label.setStyleSheet(f"""
                padding: 6px 12px;
                background-color: {self.theme.colors['error']};
                color: white;
                border-radius: 8px;
            """)

    def set_status(self, status: str):
        """Update status text"""
        self.status_label.setText(status)

    def update_camera_frame(self, pixmap):
        """Update camera feed"""
        scaled_pixmap = pixmap.scaled(
            self.camera_label.width(),
            self.camera_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.camera_label.setPixmap(scaled_pixmap)

    # Window dragging functionality
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            self.setCursor(QCursor(Qt.ClosedHandCursor))

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            event.accept()

    def enterEvent(self, event):
        """Show cursor as draggable"""
        if not self.dragging:
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def leaveEvent(self, event):
        """Reset cursor"""
        if not self.dragging:
            self.setCursor(QCursor(Qt.ArrowCursor))
