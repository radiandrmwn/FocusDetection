# Smart Focus Timer - Pomodoro Timer with Face Detection

A productivity application that combines the Pomodoro Technique with face detection to track your focus and presence. Built with PyQt5 and OpenCV.

## Features

- **Pomodoro Timer**: Classic 25-minute work sessions with 5-minute breaks
- **Automatic Presence Detection**: Pauses timer when you're away from desk
- **Face Detection**: Uses OpenCV to detect if you're at your computer
- **Eye Tracking**: Detects if you're actively looking at the screen
- **Focus Statistics**: Track total focus time, breaks, and away time
- **Focus Score**: Calculate productivity score based on presence
- **Session History**: Saves session data to track progress over time
- **Visual Feedback**: Real-time camera feed with face detection overlay

## How It Works

1. **Face Detected** → Timer runs normally
2. **Face NOT Detected (during work)** → Timer pauses automatically
3. **Face NOT Detected (during break)** → Timer continues (breaks are flexible)
4. **Eyes Detected** → Shows "FOCUSED" status for active attention tracking

## Requirements

- Python 3.8+
- Webcam
- Dependencies listed in `requirements.txt`

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python smart_focus_timer.py
```

### Controls

- **Start**: Begin the Pomodoro timer
- **Pause**: Manually pause/resume the timer
- **Reset**: Reset timer to initial state

## Statistics Tracked

- **Sessions Completed**: Number of Pomodoro sessions finished
- **Total Focus Time**: Actual time spent working while present
- **Total Break Time**: Time spent on breaks
- **Time Away**: Time away during work sessions
- **Focus Score**: Percentage of work time actually focused (0-100%)

## Project Structure

- `smart_focus_timer.py` - Main application file
  - `FaceDetector` class - Handles face and eye detection using Haar Cascades
  - `PomodoroTimer` class - Manages timer logic and statistics
  - `CameraThread` class - Handles camera capture in separate thread
  - `SmartFocusTimerGUI` class - Main PyQt GUI
- `focus_history.json` - Saves session history automatically

## Technical Details

**Face Detection:**
- Uses OpenCV Haar Cascade Classifiers
- Detects faces with high accuracy
- Tracks eye position for attention detection
- No external dependencies (no MediaPipe/TensorFlow needed)

**Timer Logic:**
- Standard Pomodoro: 25min work, 5min break
- Auto-pause only during work sessions
- Counts away time separately
- Tracks distractions (consecutive away detections)

## Customization Ideas

- Adjust work/break durations in `PomodoroTimer.__init__()`
- Add longer breaks after 4 sessions (long break)
- Add sound notifications for session completion
- Create weekly/monthly productivity reports
- Add charts and graphs for statistics visualization
- Implement different focus modes (deep work, light work, etc.)
- Add keyboard shortcuts for controls
- Export statistics to CSV

## Troubleshooting

**Camera not working:**
- Make sure your webcam is connected and not used by another application
- Try changing the camera index in `cv2.VideoCapture(0)` to `1` or `2`

**Face not detected:**
- Ensure good lighting conditions
- Face the camera directly
- Adjust `scaleFactor` and `minNeighbors` in FaceDetector if needed
- Make sure face is at least 60x60 pixels in frame

**Performance issues:**
- Close other applications using the webcam
- Reduce camera resolution if needed
- Increase update interval if computer is slow

## Why This Project?

This application is perfect for:
- Students who need to track study time
- Remote workers tracking productivity
- Anyone using the Pomodoro Technique
- Demonstrating computer vision + GUI integration
- Learning about real-time face detection

## Educational Value

**Key Concepts Demonstrated:**
- Human-Computer Interaction (HCI)
- Computer Vision (face/eye detection)
- Real-time video processing
- Multi-threaded GUI applications
- Data persistence and statistics tracking
- User feedback and visual indicators

## License

This is an educational project for Human Machine Interface course.
