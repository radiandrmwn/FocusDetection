# Changelog

All notable changes to Smart Focus Timer will be documented in this file.

## [2.0.0] - 2025-10-27

### Major Rewrite
Complete architectural overhaul with modern design patterns and enhanced features.

### Added
- **Modular Architecture**: Separated into models, services, UI, and utils
- **Theme System**: Dark and light themes with Material Design styling
- **Configuration Management**: JSON-based settings with hot-reload
- **Logging System**: Comprehensive logging to files and console
- **Data Manager**: Enhanced session history with analytics
- **Long Break Support**: Automatic long breaks every 4 work sessions
- **Daily Goals**: Set and track daily session targets
- **Data Export**: Export session history to CSV format
- **Enhanced Statistics**: Better tracking and visualization
- **Smooth Animations**: Polished UI with transitions
- **Type Hints**: Full type annotations throughout codebase

### Improved
- **Face Detection**: Better error handling and configurability
- **Camera Service**: Thread-safe with proper resource management
- **Timer Logic**: Cleaner state management with callbacks
- **UI/UX**: Modern design with better visual feedback
- **Code Quality**: Proper separation of concerns
- **Error Handling**: Robust error handling throughout
- **Documentation**: Comprehensive README and inline docs

### Changed
- Entry point changed from `smart_focus_timer.py` to `run.py`
- Configuration now in `config/settings.json` instead of hardcoded
- Session history moved to `data/` directory
- Logs now stored in `logs/` directory

### Technical
- Introduced Session, SessionType, SessionState models
- Added FaceDetectionResult data class
- Implemented Stylesheet and Theme classes
- Created reusable UI widgets (StatCard, TimerDisplay)
- Added Config and Logger utilities

## [1.0.0] - Initial Release

### Added
- Basic Pomodoro timer (25/5 minutes)
- Face detection using OpenCV Haar Cascades
- Eye tracking for focus detection
- Automatic pause on absence
- Basic statistics (sessions, focus time, breaks, away time)
- Focus score calculation
- Session history in JSON
- Simple PyQt GUI
- Real-time camera feed with detection overlay

### Features
- Work/break session management
- Presence-based timer control
- Visual feedback via camera feed
- Session persistence
