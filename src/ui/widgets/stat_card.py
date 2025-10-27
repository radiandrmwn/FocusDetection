"""
Stat Card Widget
Reusable card component for displaying statistics
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class StatCard(QWidget):
    """
    A beautiful card widget for displaying a statistic
    """

    def __init__(self, title: str, value: str = "0", icon: str = "", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.value_text = value
        self.icon_text = icon
        self.init_ui()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(12, 12, 12, 12)

        # Top row: Icon + Title
        top_layout = QHBoxLayout()

        if self.icon_text:
            self.icon = QLabel(self.icon_text)
            self.icon.setFont(QFont("Segoe UI Emoji", 16))
            self.icon.setAlignment(Qt.AlignLeft)
            top_layout.addWidget(self.icon)

        self.title = QLabel(self.title_text)
        self.title.setFont(QFont("Segoe UI", 10))
        self.title.setStyleSheet("color: #b4b4c8;")
        top_layout.addWidget(self.title)
        top_layout.addStretch()

        layout.addLayout(top_layout)

        # Value
        self.value = QLabel(self.value_text)
        self.value.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.value.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.value)

        # Subtitle (optional)
        self.subtitle = QLabel("")
        self.subtitle.setFont(QFont("Segoe UI", 10))
        self.subtitle.setStyleSheet("color: #8888a0;")
        layout.addWidget(self.subtitle)

        self.setLayout(layout)

    def set_value(self, value: str):
        """Update the value"""
        self.value.setText(value)

    def set_subtitle(self, text: str):
        """Set subtitle text"""
        self.subtitle.setText(text)
        self.subtitle.setVisible(bool(text))

    def set_color(self, color: str):
        """Set value color"""
        self.value.setStyleSheet(f"color: {color};")
