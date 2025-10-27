# Smart Focus Timer

An AI-powered Pomodoro timer with face detection that helps you stay focused. Built with PyQt5 and OpenCV.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-Educational-orange)

## 🎯 What is This?

A productivity timer that uses your webcam to detect when you're at your desk. When you leave during a work session, it automatically pauses. When you return, it resumes. Perfect for staying accountable during focused work sessions!

## ✨ Key Features

- **🍅 Pomodoro Timer** - Classic 25/5/15 minute work/break cycles
- **👁️ Face Detection** - Auto-pause when you leave your desk
- **👀 Focus Tracking** - Eye detection to measure real attention
- **📊 Daily Goals** - Track your completed sessions
- **🪟 Compact Mode** - Minimal floating window (like Microsoft Teams)
- **🎨 Clean Design** - Modern neutral black & white interface
- **💾 Data Persistence** - Saves your session history

## 📋 Requirements

- **Python 3.8+**
- **Webcam** (built-in or external)
- **Operating System**: Windows, macOS, or Linux

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python run.py
```

That's it! The app will open and request camera access.

## 📖 How to Use

### Starting Your First Session

1. **Click "▶ Start"** - Begins a 25-minute work session
2. **Stay at your desk** - Timer runs normally when your face is detected
3. **Leave your desk** - Timer automatically pauses
4. **Return** - Timer resumes when you're back
5. **Take breaks** - After each session, you'll get a short break

### Main Controls

| Button | Action |
|--------|--------|
| **▶ Start** | Begin the timer |
| **⏸ Pause** | Manually pause/resume |
| **⟲ Reset** | Reset to initial state |
| **□ Compact Mode** | Switch to mini floating window |

### Customizing Settings

**Daily Goal:**
- Set how many Pomodoro sessions you want to complete per day (1-20)

**Timer Durations:**
- **Work**: 1-60 minutes (default: 25 min)
- **Short Break**: 1-30 minutes (default: 5 min)
- **Long Break**: 5-60 minutes (default: 15 min)

> 💡 **Tip**: Long breaks happen automatically after every 4 work sessions!

## 🪟 Compact Mode

Click **"□ Compact Mode"** to minimize the app into a small floating window (220x260px) that shows:
- Timer countdown
- Live webcam feed

Perfect for keeping an eye on your progress without taking up screen space!

## 🎭 How Face Detection Works

### Presence Detection
- **Face Detected** = ✅ Timer runs (during work) or continues (during break)
- **No Face** = ⏸️ Timer pauses (only during work sessions)
- **Eyes Detected** = 🎯 Shows "FOCUSED" status (optional tracking)

### Smart Behavior
- **During WORK**: Leaving = Auto-pause ⏸️
- **During BREAK**: Leaving = Timer continues ✅ (breaks are flexible!)

## 📊 What Gets Tracked

- **Sessions Completed**: Total Pomodoro cycles finished today
- **Daily Progress**: Visual progress toward your daily goal
- **Session History**: All sessions saved to `data/sessions/`

## 🗂️ Project Structure

```
FocusDetection/
├── src/
│   ├── models/           # Timer & session logic
│   ├── services/         # Camera & face detection
│   ├── ui/              # Main window & compact mode
│   │   ├── main_window.py
│   │   ├── compact_window.py
│   │   └── widgets/     # Reusable UI components
│   └── utils/           # Config & logging
├── config/              # Settings (JSON)
├── data/                # Session history
├── logs/                # Debug logs
├── run.py              # Start here!
└── requirements.txt
```

## ⚙️ Configuration

Settings are stored in `config/settings.json`. You can edit:

```json
{
  "timer": {
    "work_duration": 1500,
    "short_break_duration": 300,
    "long_break_duration": 900,
    "daily_goal": 8
  },
  "camera": {
    "camera_index": 0,
    "fps": 10
  },
  "ui": {
    "theme": "dark",
    "window_width": 1400,
    "window_height": 900
  }
}
```

## 🔧 Troubleshooting

### Camera Issues

**Camera not detected?**
- Ensure no other app is using your webcam
- Try changing `camera_index` in settings (0, 1, or 2)
- Check camera permissions in your OS settings

**Face not detected?**
- Improve lighting conditions
- Face the camera directly
- Sit closer to the camera (at least 60x60 pixels)

### Performance Issues

**App running slowly?**
- Close other applications using the webcam
- Lower the camera FPS in settings
- Check `logs/` folder for error messages

## 🎓 Educational Context

This project was created for the **Human Machine Interface** course at **Asia University (Taiwan)** and demonstrates:

- Real-time computer vision integration
- User-centered interface design
- Multi-threaded GUI applications
- Data persistence and tracking
- Responsive user feedback systems

## 🛠️ Built With

- [PyQt5](https://pypi.org/project/PyQt5/) - Cross-platform GUI framework
- [OpenCV](https://opencv.org/) - Computer vision and face detection
- [NumPy](https://numpy.org/) - Numerical computing

## 🎨 Design Philosophy

**Neutral & Minimal**: Clean black and white design for distraction-free focus

**Unobtrusive**: Compact mode keeps the timer visible without overwhelming your workspace

**Smart Automation**: Auto-pause only when it matters (during work, not breaks)

## 📝 Tips for Best Results

1. **Good lighting** - Face detection works best in well-lit environments
2. **Face the camera** - Position yourself in front of the webcam
3. **Consistent routine** - Use the same workspace for better tracking
4. **Daily goals** - Start with realistic targets (4-6 sessions/day)
5. **Breaks matter** - Don't skip them! They're essential for productivity

## 🔮 Future Enhancements

- 🔲 Sound notifications when sessions complete
- 🔲 Productivity charts and analytics
- 🔲 Weekly/monthly reports
- 🔲 System tray integration
- 🔲 Multiple theme options
- 🔲 Export statistics to CSV
