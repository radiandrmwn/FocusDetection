"""
Configuration Management
Handles application settings and user preferences
"""

import json
import os
from pathlib import Path
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class Config:
    """Application configuration manager"""

    DEFAULT_CONFIG = {
        # Timer settings
        'timer': {
            'work_duration': 25,  # minutes
            'short_break_duration': 5,
            'long_break_duration': 15,
            'sessions_until_long_break': 4,
            'daily_goal': 8
        },

        # Camera settings
        'camera': {
            'camera_index': 0,
            'fps': 30,
            'width': 640,
            'height': 480
        },

        # Face detection settings
        'detection': {
            'face_scale_factor': 1.1,
            'face_min_neighbors': 5,
            'face_min_size': [60, 60],
            'eye_scale_factor': 1.05,
            'eye_min_neighbors': 5,
            'eye_min_size': [20, 20],
            'min_eyes_for_focus': 2
        },

        # UI settings
        'ui': {
            'theme': 'dark',  # 'dark' or 'light'
            'show_camera_feed': True,
            'minimize_to_tray': True,
            'start_minimized': False,
            'window_width': 1400,
            'window_height': 800
        },

        # Notification settings
        'notifications': {
            'sound_enabled': True,
            'desktop_notifications': True,
            'break_reminders': True,
            'session_complete_sound': 'default'
        },

        # Data settings
        'data': {
            'auto_save': True,
            'data_retention_days': 90,
            'export_format': 'csv'
        }
    }

    def __init__(self, config_file: str = "config/settings.json"):
        """Initialize configuration manager"""
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.settings: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.settings = self._merge_configs(
                        self.DEFAULT_CONFIG.copy(),
                        loaded_config
                    )
                    logger.info("Configuration loaded successfully")
            else:
                logger.info("No config file found, using defaults")
                self.settings = self.DEFAULT_CONFIG.copy()
                self.save()
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            self.settings = self.DEFAULT_CONFIG.copy()

    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Example: config.get('timer.work_duration')
        """
        keys = key.split('.')
        value = self.settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation

        Example: config.set('timer.work_duration', 30)
        """
        keys = key.split('.')
        current = self.settings

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self.save()
        logger.info(f"Config updated: {key} = {value}")

    def get_section(self, section: str) -> Dict:
        """Get entire configuration section"""
        return self.settings.get(section, {}).copy()

    def update_section(self, section: str, updates: Dict):
        """Update multiple values in a section"""
        if section not in self.settings:
            self.settings[section] = {}

        self.settings[section].update(updates)
        self.save()
        logger.info(f"Config section updated: {section}")

    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.settings = self.DEFAULT_CONFIG.copy()
        self.save()
        logger.info("Configuration reset to defaults")

    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Recursively merge two configuration dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result


# Global configuration instance
_config_instance = None


def get_config() -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
