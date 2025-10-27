"""
UI Theme System
Modern Material Design-inspired themes for the application
"""

from typing import Dict
from enum import Enum


class ThemeMode(Enum):
    """Theme modes"""
    DARK = "dark"
    LIGHT = "light"


class Theme:
    """Theme configuration with colors and styles"""

    def __init__(self, mode: ThemeMode):
        self.mode = mode
        self.colors = DARK_THEME if mode == ThemeMode.DARK else LIGHT_THEME


# Dark Theme Colors - Neutral Black & White
DARK_THEME = {
    # Background colors
    'bg_primary': '#0a0a0a',
    'bg_secondary': '#1a1a1a',
    'bg_tertiary': '#2a2a2a',
    'bg_elevated': '#2f2f2f',

    # Text colors
    'text_primary': '#ffffff',
    'text_secondary': '#b0b0b0',
    'text_tertiary': '#808080',
    'text_disabled': '#505050',

    # Brand colors - Neutral grayscale
    'primary': '#ffffff',
    'primary_hover': '#e0e0e0',
    'primary_light': '#f5f5f5',

    # Status colors - Grayscale
    'success': '#d0d0d0',
    'success_hover': '#b8b8b8',
    'warning': '#a0a0a0',
    'warning_hover': '#888888',
    'error': '#707070',
    'error_hover': '#606060',
    'info': '#c0c0c0',
    'info_hover': '#a8a8a8',

    # Session colors - Grayscale
    'work': '#e8e8e8',
    'work_hover': '#d0d0d0',
    'break': '#b0b0b0',
    'break_hover': '#989898',
    'focus': '#d0d0d0',
    'away': '#707070',

    # UI elements
    'border': '#404040',
    'border_light': '#505050',
    'shadow': 'rgba(0, 0, 0, 0.5)',
    'overlay': 'rgba(0, 0, 0, 0.7)',

    # Special
    'transparent': 'transparent',
}

# Light Theme Colors
LIGHT_THEME = {
    # Background colors
    'bg_primary': '#ffffff',
    'bg_secondary': '#f5f5f7',
    'bg_tertiary': '#e8e8ed',
    'bg_elevated': '#ffffff',

    # Text colors
    'text_primary': '#1a1a1a',
    'text_secondary': '#4a4a4a',
    'text_tertiary': '#6a6a6a',
    'text_disabled': '#a0a0a0',

    # Brand colors
    'primary': '#7c3aed',
    'primary_hover': '#6d28d9',
    'primary_light': '#8b5cf6',

    # Status colors
    'success': '#059669',
    'success_hover': '#047857',
    'warning': '#d97706',
    'warning_hover': '#b45309',
    'error': '#dc2626',
    'error_hover': '#b91c1c',
    'info': '#2563eb',
    'info_hover': '#1d4ed8',

    # Session colors
    'work': '#2563eb',
    'work_hover': '#1d4ed8',
    'break': '#d97706',
    'break_hover': '#b45309',
    'focus': '#059669',
    'away': '#dc2626',

    # UI elements
    'border': '#d0d0d8',
    'border_light': '#e0e0e8',
    'shadow': 'rgba(0, 0, 0, 0.1)',
    'overlay': 'rgba(0, 0, 0, 0.5)',

    # Special
    'transparent': 'transparent',
}


class Stylesheet:
    """Generates Qt stylesheets based on theme"""

    def __init__(self, theme: Theme):
        self.theme = theme
        self.c = theme.colors  # Shorthand for colors

    def get_main_stylesheet(self) -> str:
        """Get main application stylesheet"""
        return f"""
        QMainWindow {{
            background-color: {self.c['bg_primary']};
        }}

        QWidget {{
            background-color: {self.c['bg_primary']};
            color: {self.c['text_primary']};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}

        /* Group Boxes */
        QGroupBox {{
            background-color: {self.c['bg_secondary']};
            border: 2px solid {self.c['border']};
            border-radius: 10px;
            margin-top: 10px;
            padding: 12px;
            padding-top: 20px;
            font-size: 13px;
            font-weight: bold;
            color: {self.c['text_primary']};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 4px 10px;
            background-color: {self.c['primary']};
            border-radius: 5px;
            color: #000000;
            font-size: 12px;
            font-weight: bold;
        }}

        /* Labels */
        QLabel {{
            background-color: transparent;
            color: {self.c['text_primary']};
        }}

        /* Progress Bars */
        QProgressBar {{
            border: 2px solid {self.c['border']};
            border-radius: 8px;
            text-align: center;
            background-color: {self.c['bg_tertiary']};
            color: {self.c['text_primary']};
            font-weight: bold;
            height: 30px;
        }}

        QProgressBar::chunk {{
            background-color: {self.c['primary']};
            border-radius: 6px;
        }}

        /* Spin Boxes */
        QSpinBox {{
            background-color: {self.c['bg_tertiary']};
            border: 2px solid {self.c['border']};
            border-radius: 8px;
            padding: 8px;
            padding-right: 25px;
            color: {self.c['text_primary']};
            font-size: 13px;
            min-width: 100px;
        }}

        QSpinBox:focus {{
            border: 2px solid {self.c['primary']};
        }}

        QSpinBox::up-button {{
            subcontrol-origin: border;
            subcontrol-position: top right;
            background-color: {self.c['bg_tertiary']};
            border-top-right-radius: 5px;
            border-left: 1px solid {self.c['border']};
            width: 20px;
            margin-right: 1px;
            margin-top: 1px;
        }}

        QSpinBox::up-button:hover {{
            background-color: {self.c['bg_elevated']};
        }}

        QSpinBox::down-button {{
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            background-color: {self.c['bg_tertiary']};
            border-bottom-right-radius: 5px;
            border-left: 1px solid {self.c['border']};
            width: 20px;
            margin-right: 1px;
            margin-bottom: 1px;
        }}

        QSpinBox::down-button:hover {{
            background-color: {self.c['bg_elevated']};
        }}

        QSpinBox::up-arrow {{
            width: 0px;
            height: 0px;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-bottom: 6px solid {self.c['text_primary']};
        }}

        QSpinBox::down-arrow {{
            width: 0px;
            height: 0px;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {self.c['text_primary']};
        }}

        /* Sliders */
        QSlider::groove:horizontal {{
            border: none;
            height: 8px;
            background: {self.c['bg_tertiary']};
            border-radius: 4px;
        }}

        QSlider::handle:horizontal {{
            background: {self.c['primary']};
            width: 20px;
            height: 20px;
            margin: -6px 0;
            border-radius: 10px;
        }}

        QSlider::handle:horizontal:hover {{
            background: {self.c['primary_hover']};
        }}

        /* Combo Boxes */
        QComboBox {{
            background-color: {self.c['bg_tertiary']};
            border: 2px solid {self.c['border']};
            border-radius: 8px;
            padding: 8px;
            color: {self.c['text_primary']};
            min-width: 120px;
        }}

        QComboBox:focus {{
            border: 2px solid {self.c['primary']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {self.c['bg_secondary']};
            border: 2px solid {self.c['border']};
            selection-background-color: {self.c['primary']};
            color: {self.c['text_primary']};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 2px solid {self.c['border']};
            border-radius: 8px;
            background-color: {self.c['bg_secondary']};
            padding: 10px;
        }}

        QTabBar::tab {{
            background-color: {self.c['bg_tertiary']};
            border: 2px solid {self.c['border']};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 10px 20px;
            margin-right: 2px;
            color: {self.c['text_secondary']};
        }}

        QTabBar::tab:selected {{
            background-color: {self.c['primary']};
            color: white;
        }}

        QTabBar::tab:hover {{
            background-color: {self.c['primary_light']};
            color: white;
        }}

        /* Scroll Bar */
        QScrollBar:vertical {{
            background: {self.c['bg_tertiary']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background: {self.c['primary']};
            border-radius: 6px;
            min-height: 20px;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """

    def get_button_style(self, button_type: str = "primary") -> str:
        """Get button stylesheet"""
        styles = {
            'primary': (self.c['primary'], self.c['primary_hover'], '#000000'),
            'success': (self.c['success'], self.c['success_hover'], '#000000'),
            'warning': (self.c['warning'], self.c['warning_hover'], '#000000'),
            'error': (self.c['error'], self.c['error_hover'], '#ffffff'),
        }

        bg, hover, text_color = styles.get(button_type, styles['primary'])

        return f"""
        QPushButton {{
            background-color: {bg};
            color: {text_color};
            border: none;
            border-radius: 10px;
            padding: 12px 24px;
            font-size: 14px;
            font-weight: bold;
        }}

        QPushButton:hover {{
            background-color: {hover};
        }}

        QPushButton:pressed {{
            background-color: {hover};
            padding-top: 14px;
            padding-bottom: 10px;
        }}

        QPushButton:disabled {{
            background-color: {self.c['bg_tertiary']};
            color: {self.c['text_disabled']};
        }}
        """

    def get_card_style(self) -> str:
        """Get card/panel stylesheet"""
        return f"""
        background-color: {self.c['bg_secondary']};
        border: 2px solid {self.c['border']};
        border-radius: 12px;
        padding: 20px;
        """


def get_theme(mode: ThemeMode = ThemeMode.DARK) -> Theme:
    """Get theme instance"""
    return Theme(mode)


def get_stylesheet(theme: Theme) -> Stylesheet:
    """Get stylesheet generator for theme"""
    return Stylesheet(theme)
