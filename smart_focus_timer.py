"""
Smart Focus Timer - Pomodoro Timer with Face Detection
A PyQt + OpenCV application that tracks your focus using face detection
Automatically pauses when you're away and resumes when you return
"""

import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QProgressBar,
                             QGroupBox, QGridLayout, QTabWidget, QSlider, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap, QFont
from datetime import datetime, timedelta
import json
import os


class FaceDetector:
    """Handles face detection using OpenCV Haar Cascades"""

    def __init__(self):
        # Load the pre-trained face detection cascade
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        # For better detection, also load eye cascade
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )

    def detect_face(self, frame):
        """Detect if a face is present in the frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        face_detected = len(faces) > 0
        looking_at_screen = False

        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Check for eyes in face region (indicates looking at screen)
            roi_gray = gray[y:y + h, x:x + w]

            # More strict eye detection parameters
            eyes = self.eye_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.05,  # More sensitive to scale
                minNeighbors=5,    # Increased from 3 to 5 (more strict)
                minSize=(20, 20)   # Minimum eye size
            )

            # Require exactly 2 eyes detected (or more, but we focus on best 2)
            # Filter eyes to only those in upper half of face (where eyes should be)
            valid_eyes = []
            face_upper_half = h // 2

            for (ex, ey, ew, eh) in eyes:
                # Eyes should be in upper half of face
                if ey < face_upper_half:
                    # Eyes should have reasonable aspect ratio (not too tall/wide)
                    aspect_ratio = ew / eh
                    if 0.8 < aspect_ratio < 2.5:
                        valid_eyes.append((ex, ey, ew, eh))

            # Only consider "focused" if we detect at least 2 valid eyes
            if len(valid_eyes) >= 2:
                looking_at_screen = True
                # Draw eye indicators (only first 2)
                for (ex, ey, ew, eh) in valid_eyes[:2]:
                    cv2.circle(frame, (x + ex + ew // 2, y + ey + eh // 2), 5, (255, 0, 0), -1)
                    # Draw small rectangle around eyes for debugging
                    cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (255, 0, 0), 1)

            # Add status text
            status = "FOCUSED" if looking_at_screen else "PRESENT"
            color = (0, 255, 0) if looking_at_screen else (0, 165, 255)
            cv2.putText(frame, status, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                       0.6, color, 2)

        return face_detected, looking_at_screen, frame


class PomodoroTimer:
    """Handles Pomodoro timer logic"""

    def __init__(self, work_duration=25, break_duration=5, daily_goal=8):
        self.work_duration = work_duration * 60  # Convert to seconds
        self.break_duration = break_duration * 60
        self.time_remaining = self.work_duration
        self.is_work_session = True
        self.is_running = False
        self.is_paused = False
        self.sessions_completed = 0
        self.daily_goal = daily_goal  # Target sessions per day

        # Statistics
        self.total_focus_time = 0  # seconds
        self.total_break_time = 0
        self.total_away_time = 0
        self.distraction_count = 0
        self.session_start_time = None
        self.daily_sessions = []
        self.today_sessions = 0  # Sessions completed today

    def set_durations(self, work_minutes, break_minutes):
        """Update work and break durations (only when timer is not running)"""
        if not self.is_running:
            self.work_duration = work_minutes * 60
            self.break_duration = break_minutes * 60
            if self.is_work_session:
                self.time_remaining = self.work_duration
            else:
                self.time_remaining = self.break_duration
            return True
        return False

    def set_daily_goal(self, goal):
        """Set daily goal for sessions"""
        self.daily_goal = goal

    def get_daily_progress(self):
        """Get progress towards daily goal as percentage"""
        if self.daily_goal == 0:
            return 100
        return min(100, int((self.today_sessions / self.daily_goal) * 100))

    def start(self):
        """Start the timer"""
        self.is_running = True
        self.is_paused = False
        if self.session_start_time is None:
            self.session_start_time = datetime.now()

    def pause(self):
        """Pause the timer"""
        self.is_paused = True

    def resume(self):
        """Resume the timer"""
        self.is_paused = False

    def stop(self):
        """Stop the timer"""
        self.is_running = False
        self.is_paused = False

    def reset(self):
        """Reset the timer to work session"""
        self.is_work_session = True
        self.time_remaining = self.work_duration
        self.is_running = False
        self.is_paused = False
        self.session_start_time = None

    def tick(self, user_present=True):
        """Decrease timer by 1 second"""
        if not self.is_running:
            return

        if user_present and not self.is_paused:
            self.time_remaining -= 1

            # Track statistics
            if self.is_work_session:
                self.total_focus_time += 1
            else:
                self.total_break_time += 1

            # Check if timer completed
            if self.time_remaining <= 0:
                self.complete_session()

        elif not user_present and self.is_work_session:
            # User is away during work session - count as away time
            self.total_away_time += 1

    def complete_session(self):
        """Complete current session and switch to next"""
        if self.is_work_session:
            self.sessions_completed += 1
            self.today_sessions += 1  # Increment today's count
            self.daily_sessions.append({
                'date': datetime.now().isoformat(),
                'duration': self.work_duration,
                'focus_time': self.work_duration,
                'type': 'work'
            })

        # Switch session type
        self.is_work_session = not self.is_work_session

        if self.is_work_session:
            self.time_remaining = self.work_duration
        else:
            self.time_remaining = self.break_duration

    def get_time_display(self):
        """Get formatted time string"""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_progress_percentage(self):
        """Get progress as percentage"""
        if self.is_work_session:
            total = self.work_duration
        else:
            total = self.break_duration

        return int((1 - self.time_remaining / total) * 100)

    def get_focus_score(self):
        """Calculate focus score (0-100)"""
        total_work_time = self.total_focus_time + self.total_away_time
        if total_work_time == 0:
            return 100

        focus_percentage = (self.total_focus_time / total_work_time) * 100
        return min(100, int(focus_percentage))


class CameraThread(QThread):
    """Thread for handling camera capture and face detection"""
    frame_ready = pyqtSignal(np.ndarray)
    face_status = pyqtSignal(bool, bool)  # face_detected, looking_at_screen

    def __init__(self):
        super().__init__()
        self.running = False
        self.face_detector = FaceDetector()

    def run(self):
        """Main camera loop"""
        cap = cv2.VideoCapture(0)
        self.running = True

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)  # Mirror the frame

            # Detect face
            face_detected, looking_at_screen, frame = self.face_detector.detect_face(frame)

            # Emit signals
            self.face_status.emit(face_detected, looking_at_screen)
            self.frame_ready.emit(frame)

        cap.release()

    def stop(self):
        """Stop the camera thread"""
        self.running = False
        self.wait()


class SmartFocusTimerGUI(QMainWindow):
    """Main GUI for Smart Focus Timer application"""

    def __init__(self):
        super().__init__()
        self.timer = PomodoroTimer(work_duration=25, break_duration=5)
        self.user_present = False
        self.looking_at_screen = False
        self.away_count = 0
        self.init_ui()
        self.init_camera()

        # Timer for updating display
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second

        # Load session history
        self.load_history()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Smart Focus Timer - Pomodoro with Face Detection")
        self.setGeometry(100, 100, 1400, 800)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Left side - Timer and controls
        left_layout = QVBoxLayout()

        # Timer display
        timer_group = QGroupBox("Pomodoro Timer")
        timer_layout = QVBoxLayout()

        # Session type label
        self.session_label = QLabel("WORK SESSION")
        self.session_label.setAlignment(Qt.AlignCenter)
        self.session_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.session_label.setStyleSheet("color: #2ecc71; padding: 10px;")
        timer_layout.addWidget(self.session_label)

        # Time display
        self.time_label = QLabel("25:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 72, QFont.Bold))
        self.time_label.setStyleSheet("color: #3498db; padding: 20px;")
        timer_layout.addWidget(self.time_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3498db;
                border-radius: 5px;
                text-align: center;
                height: 30px;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
            }
        """)
        timer_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready to start")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 14))
        self.status_label.setStyleSheet("padding: 10px;")
        timer_layout.addWidget(self.status_label)

        timer_group.setLayout(timer_layout)
        left_layout.addWidget(timer_group)

        # Control buttons
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶ Start")
        self.start_btn.setFont(QFont("Arial", 14))
        self.start_btn.clicked.connect(self.start_timer)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        button_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setFont(QFont("Arial", 14))
        self.pause_btn.clicked.connect(self.pause_timer)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #e67e22; }
            QPushButton:disabled { background-color: #bdc3c7; }
        """)
        button_layout.addWidget(self.pause_btn)

        self.reset_btn = QPushButton("⟲ Reset")
        self.reset_btn.setFont(QFont("Arial", 14))
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 15px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        button_layout.addWidget(self.reset_btn)

        left_layout.addLayout(button_layout)

        # Statistics panel
        stats_group = QGroupBox("Session Statistics")
        stats_layout = QGridLayout()

        # Sessions completed
        stats_layout.addWidget(QLabel("Sessions Completed:"), 0, 0)
        self.sessions_label = QLabel("0")
        self.sessions_label.setFont(QFont("Arial", 14, QFont.Bold))
        stats_layout.addWidget(self.sessions_label, 0, 1)

        # Focus time
        stats_layout.addWidget(QLabel("Total Focus Time:"), 1, 0)
        self.focus_time_label = QLabel("0m")
        self.focus_time_label.setFont(QFont("Arial", 14, QFont.Bold))
        stats_layout.addWidget(self.focus_time_label, 1, 1)

        # Break time
        stats_layout.addWidget(QLabel("Total Break Time:"), 2, 0)
        self.break_time_label = QLabel("0m")
        self.break_time_label.setFont(QFont("Arial", 14, QFont.Bold))
        stats_layout.addWidget(self.break_time_label, 2, 1)

        # Away time
        stats_layout.addWidget(QLabel("Time Away:"), 3, 0)
        self.away_time_label = QLabel("0m")
        self.away_time_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.away_time_label.setStyleSheet("color: #e74c3c;")
        stats_layout.addWidget(self.away_time_label, 3, 1)

        # Focus score
        stats_layout.addWidget(QLabel("Focus Score:"), 4, 0)
        self.focus_score_label = QLabel("100%")
        self.focus_score_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.focus_score_label.setStyleSheet("color: #2ecc71;")
        stats_layout.addWidget(self.focus_score_label, 4, 1)

        stats_group.setLayout(stats_layout)
        left_layout.addWidget(stats_group)

        # Daily Goal Tracker
        goal_group = QGroupBox("Daily Goal")
        goal_layout = QVBoxLayout()

        # Goal progress bar
        goal_progress_layout = QHBoxLayout()
        goal_progress_layout.addWidget(QLabel("Progress:"))
        self.goal_progress_bar = QProgressBar()
        self.goal_progress_bar.setMaximum(100)
        self.goal_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #9b59b6;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #9b59b6;
            }
        """)
        goal_progress_layout.addWidget(self.goal_progress_bar)
        goal_layout.addLayout(goal_progress_layout)

        # Goal counter
        self.goal_label = QLabel("0 / 8 sessions")
        self.goal_label.setAlignment(Qt.AlignCenter)
        self.goal_label.setFont(QFont("Arial", 12))
        goal_layout.addWidget(self.goal_label)

        # Goal slider
        goal_slider_layout = QHBoxLayout()
        goal_slider_layout.addWidget(QLabel("Daily Target:"))
        self.goal_spinbox = QSpinBox()
        self.goal_spinbox.setMinimum(1)
        self.goal_spinbox.setMaximum(20)
        self.goal_spinbox.setValue(8)
        self.goal_spinbox.setSuffix(" sessions")
        self.goal_spinbox.valueChanged.connect(self.update_goal)
        goal_slider_layout.addWidget(self.goal_spinbox)
        goal_layout.addLayout(goal_slider_layout)

        goal_group.setLayout(goal_layout)
        left_layout.addWidget(goal_group)

        # Timer Settings
        settings_group = QGroupBox("Timer Settings")
        settings_layout = QGridLayout()

        # Work duration slider
        settings_layout.addWidget(QLabel("Work Duration:"), 0, 0)
        self.work_spinbox = QSpinBox()
        self.work_spinbox.setMinimum(1)
        self.work_spinbox.setMaximum(60)
        self.work_spinbox.setValue(25)
        self.work_spinbox.setSuffix(" min")
        self.work_spinbox.valueChanged.connect(self.update_timer_settings)
        settings_layout.addWidget(self.work_spinbox, 0, 1)

        # Break duration slider
        settings_layout.addWidget(QLabel("Break Duration:"), 1, 0)
        self.break_spinbox = QSpinBox()
        self.break_spinbox.setMinimum(1)
        self.break_spinbox.setMaximum(30)
        self.break_spinbox.setValue(5)
        self.break_spinbox.setSuffix(" min")
        self.break_spinbox.valueChanged.connect(self.update_timer_settings)
        settings_layout.addWidget(self.break_spinbox, 1, 1)

        # Info label
        self.settings_info = QLabel("⚠️ Can only change when timer is stopped")
        self.settings_info.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        self.settings_info.setAlignment(Qt.AlignCenter)
        self.settings_info.setVisible(False)
        settings_layout.addWidget(self.settings_info, 2, 0, 1, 2)

        settings_group.setLayout(settings_layout)
        left_layout.addWidget(settings_group)

        main_layout.addLayout(left_layout, 2)

        # Right side - Camera feed and presence detection
        right_layout = QVBoxLayout()

        # Camera feed
        camera_label = QLabel("Camera Feed - Face Detection")
        camera_label.setAlignment(Qt.AlignCenter)
        camera_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(camera_label)

        self.camera_label = QLabel()
        self.camera_label.setFixedSize(640, 480)
        self.camera_label.setStyleSheet("border: 3px solid #3498db; background-color: #2c3e50;")
        right_layout.addWidget(self.camera_label)

        # Presence indicator
        presence_group = QGroupBox("Presence Detection")
        presence_layout = QVBoxLayout()

        self.presence_indicator = QLabel("● AWAY")
        self.presence_indicator.setAlignment(Qt.AlignCenter)
        self.presence_indicator.setFont(QFont("Arial", 20, QFont.Bold))
        self.presence_indicator.setStyleSheet("""
            padding: 20px;
            background-color: #e74c3c;
            color: white;
            border-radius: 10px;
        """)
        presence_layout.addWidget(self.presence_indicator)

        self.attention_indicator = QLabel("Looking: Unknown")
        self.attention_indicator.setAlignment(Qt.AlignCenter)
        self.attention_indicator.setFont(QFont("Arial", 14))
        presence_layout.addWidget(self.attention_indicator)

        info_label = QLabel(
            "✓ Face detected = Timer runs\n"
            "✗ No face = Timer pauses (work sessions only)\n"
            "👁 Eyes detected = Actively focused"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("padding: 10px; color: #7f8c8d;")
        presence_layout.addWidget(info_label)

        presence_group.setLayout(presence_layout)
        right_layout.addWidget(presence_group)

        main_layout.addLayout(right_layout, 1)

    def init_camera(self):
        """Initialize camera thread"""
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.update_camera_feed)
        self.camera_thread.face_status.connect(self.update_face_status)
        self.camera_thread.start()

    def update_camera_feed(self, frame):
        """Update camera feed display"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.camera_label.setPixmap(pixmap.scaled(
            self.camera_label.width(),
            self.camera_label.height(),
            Qt.KeepAspectRatio
        ))

    def update_face_status(self, face_detected, looking_at_screen):
        """Update face detection status"""
        self.user_present = face_detected
        self.looking_at_screen = looking_at_screen

        if face_detected:
            self.presence_indicator.setText("● PRESENT")
            self.presence_indicator.setStyleSheet("""
                padding: 20px;
                background-color: #2ecc71;
                color: white;
                border-radius: 10px;
            """)
            self.away_count = 0

            if looking_at_screen:
                self.attention_indicator.setText("👁 Looking: FOCUSED")
                self.attention_indicator.setStyleSheet("color: #2ecc71; font-weight: bold;")
            else:
                self.attention_indicator.setText("👁 Looking: PRESENT")
                self.attention_indicator.setStyleSheet("color: #f39c12;")
        else:
            self.presence_indicator.setText("● AWAY")
            self.presence_indicator.setStyleSheet("""
                padding: 20px;
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
            """)
            self.attention_indicator.setText("👁 Looking: NOT DETECTED")
            self.attention_indicator.setStyleSheet("color: #e74c3c;")

            # Count consecutive away detections
            if self.timer.is_running and self.timer.is_work_session:
                self.away_count += 1
                if self.away_count == 3:  # After 3 seconds away
                    self.timer.distraction_count += 1

    def start_timer(self):
        """Start the timer"""
        self.timer.start()
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.update_status()

    def pause_timer(self):
        """Pause/Resume the timer"""
        if self.timer.is_paused:
            self.timer.resume()
            self.pause_btn.setText("⏸ Pause")
        else:
            self.timer.pause()
            self.pause_btn.setText("▶ Resume")
        self.update_status()

    def reset_timer(self):
        """Reset the timer"""
        self.timer.reset()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Pause")
        self.settings_info.setVisible(False)
        self.update_display()
        self.update_status()

    def update_timer_settings(self):
        """Update timer durations from spinboxes"""
        work_min = self.work_spinbox.value()
        break_min = self.break_spinbox.value()

        success = self.timer.set_durations(work_min, break_min)
        if success:
            self.settings_info.setVisible(False)
            self.update_display()
        else:
            # Show warning if timer is running
            self.settings_info.setVisible(True)

    def update_goal(self):
        """Update daily goal from spinbox"""
        goal = self.goal_spinbox.value()
        self.timer.set_daily_goal(goal)
        self.update_goal_display()

    def update_goal_display(self):
        """Update the daily goal display"""
        progress = self.timer.get_daily_progress()
        self.goal_progress_bar.setValue(progress)
        self.goal_label.setText(f"{self.timer.today_sessions} / {self.timer.daily_goal} sessions")

        # Change color based on progress
        if progress >= 100:
            self.goal_progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #2ecc71;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    font-size: 12px;
                }
                QProgressBar::chunk {
                    background-color: #2ecc71;
                }
            """)
            self.goal_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        elif progress >= 75:
            self.goal_progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #f39c12;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    font-size: 12px;
                }
                QProgressBar::chunk {
                    background-color: #f39c12;
                }
            """)
            self.goal_label.setStyleSheet("color: #f39c12;")
        else:
            self.goal_progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #9b59b6;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    font-size: 12px;
                }
                QProgressBar::chunk {
                    background-color: #9b59b6;
                }
            """)
            self.goal_label.setStyleSheet("color: black;")

    def update_display(self):
        """Update all display elements"""
        # Tick the timer
        self.timer.tick(self.user_present)

        # Update time display
        self.time_label.setText(self.timer.get_time_display())

        # Update progress bar
        self.progress_bar.setValue(self.timer.get_progress_percentage())

        # Update session type
        if self.timer.is_work_session:
            self.session_label.setText("WORK SESSION")
            self.session_label.setStyleSheet("color: #2ecc71; padding: 10px; font-weight: bold;")
            self.time_label.setStyleSheet("color: #3498db; padding: 20px;")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #3498db;
                    border-radius: 5px;
                    text-align: center;
                    height: 30px;
                    font-size: 14px;
                }
                QProgressBar::chunk {
                    background-color: #3498db;
                }
            """)
        else:
            self.session_label.setText("BREAK TIME")
            self.session_label.setStyleSheet("color: #f39c12; padding: 10px; font-weight: bold;")
            self.time_label.setStyleSheet("color: #f39c12; padding: 20px;")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #f39c12;
                    border-radius: 5px;
                    text-align: center;
                    height: 30px;
                    font-size: 14px;
                }
                QProgressBar::chunk {
                    background-color: #f39c12;
                }
            """)

        # Update statistics
        self.sessions_label.setText(str(self.timer.sessions_completed))
        self.focus_time_label.setText(f"{self.timer.total_focus_time // 60}m")
        self.break_time_label.setText(f"{self.timer.total_break_time // 60}m")
        self.away_time_label.setText(f"{self.timer.total_away_time // 60}m")

        focus_score = self.timer.get_focus_score()
        self.focus_score_label.setText(f"{focus_score}%")

        # Color code focus score
        if focus_score >= 80:
            self.focus_score_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        elif focus_score >= 60:
            self.focus_score_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        else:
            self.focus_score_label.setStyleSheet("color: #e74c3c; font-weight: bold;")

        # Update daily goal display
        self.update_goal_display()

        # Update status
        self.update_status()

    def update_status(self):
        """Update status label"""
        if not self.timer.is_running:
            self.status_label.setText("Ready to start")
        elif self.timer.is_paused:
            self.status_label.setText("⏸ Paused (manual)")
        elif not self.user_present and self.timer.is_work_session:
            self.status_label.setText("⏸ Paused - You're away!")
        elif self.timer.is_work_session:
            if self.looking_at_screen:
                self.status_label.setText("✓ Working - Focused!")
            else:
                self.status_label.setText("✓ Working - Present")
        else:
            self.status_label.setText("☕ Break time - Relax!")

    def load_history(self):
        """Load session history from file"""
        try:
            if os.path.exists('focus_history.json'):
                with open('focus_history.json', 'r') as f:
                    data = json.load(f)
                    self.timer.daily_sessions = data.get('sessions', [])
        except Exception as e:
            print(f"Error loading history: {e}")

    def save_history(self):
        """Save session history to file"""
        try:
            data = {
                'sessions': self.timer.daily_sessions,
                'last_updated': datetime.now().isoformat()
            }
            with open('focus_history.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def closeEvent(self, event):
        """Handle window close event"""
        self.save_history()
        self.camera_thread.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = SmartFocusTimerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
