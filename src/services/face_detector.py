"""
Face Detection Service
Handles face and eye detection using OpenCV Haar Cascades
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class FaceDetectionResult:
    """Data class for face detection results"""

    def __init__(self, face_detected: bool, focused: bool,
                 faces: List[Tuple[int, int, int, int]] = None,
                 eyes: List[Tuple[int, int, int, int]] = None):
        self.face_detected = face_detected
        self.focused = focused
        self.faces = faces or []
        self.eyes = eyes or []
        self.confidence = 1.0 if focused else 0.5 if face_detected else 0.0


class FaceDetector:
    """
    Enhanced face detector with configurable parameters and better error handling
    """

    def __init__(self,
                 face_scale_factor: float = 1.1,
                 face_min_neighbors: int = 5,
                 face_min_size: Tuple[int, int] = (60, 60),
                 eye_scale_factor: float = 1.05,
                 eye_min_neighbors: int = 5,
                 eye_min_size: Tuple[int, int] = (20, 20),
                 min_eyes_for_focus: int = 2):
        """
        Initialize face detector with configurable parameters

        Args:
            face_scale_factor: How much the image size is reduced at each scale
            face_min_neighbors: How many neighbors each candidate rectangle should have
            face_min_size: Minimum possible face size
            eye_scale_factor: Scale factor for eye detection
            eye_min_neighbors: Min neighbors for eye detection
            eye_min_size: Minimum eye size
            min_eyes_for_focus: Minimum eyes detected to consider user focused
        """
        self.face_scale_factor = face_scale_factor
        self.face_min_neighbors = face_min_neighbors
        self.face_min_size = face_min_size
        self.eye_scale_factor = eye_scale_factor
        self.eye_min_neighbors = eye_min_neighbors
        self.eye_min_size = eye_min_size
        self.min_eyes_for_focus = min_eyes_for_focus

        # Load cascades
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )

            if self.face_cascade.empty() or self.eye_cascade.empty():
                raise ValueError("Failed to load Haar cascades")

            logger.info("Face detector initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize face detector: {e}")
            raise

    def detect(self, frame: np.ndarray) -> Tuple[FaceDetectionResult, np.ndarray]:
        """
        Detect faces and determine focus state

        Args:
            frame: Input image frame (BGR format)

        Returns:
            Tuple of (FaceDetectionResult, annotated_frame)
        """
        if frame is None or frame.size == 0:
            logger.warning("Received empty frame")
            return FaceDetectionResult(False, False), frame

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.face_scale_factor,
                minNeighbors=self.face_min_neighbors,
                minSize=self.face_min_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            face_detected = len(faces) > 0
            looking_at_screen = False
            all_valid_eyes = []

            # Process each detected face
            for (x, y, w, h) in faces:
                # Draw face rectangle
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Detect eyes in face region
                roi_gray = gray[y:y + h, x:x + w]
                eyes = self.eye_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=self.eye_scale_factor,
                    minNeighbors=self.eye_min_neighbors,
                    minSize=self.eye_min_size
                )

                # Filter valid eyes (upper half of face, reasonable aspect ratio)
                valid_eyes = self._filter_valid_eyes(eyes, h)
                all_valid_eyes.extend([(x + ex, y + ey, ew, eh)
                                      for (ex, ey, ew, eh) in valid_eyes])

                # Check if user is focused
                if len(valid_eyes) >= self.min_eyes_for_focus:
                    looking_at_screen = True
                    self._draw_eyes(frame, x, y, valid_eyes)

                # Draw status text
                status = "FOCUSED" if looking_at_screen else "PRESENT"
                color = (0, 255, 0) if looking_at_screen else (0, 165, 255)
                cv2.putText(frame, status, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            result = FaceDetectionResult(
                face_detected=face_detected,
                focused=looking_at_screen,
                faces=faces.tolist() if len(faces) > 0 else [],
                eyes=all_valid_eyes
            )

            return result, frame

        except Exception as e:
            logger.error(f"Error during face detection: {e}")
            return FaceDetectionResult(False, False), frame

    def _filter_valid_eyes(self, eyes: np.ndarray, face_height: int) -> List[Tuple]:
        """Filter eyes to only valid detections in upper half of face"""
        valid_eyes = []
        face_upper_half = face_height // 2

        for (ex, ey, ew, eh) in eyes:
            # Eyes should be in upper half of face
            if ey < face_upper_half:
                # Eyes should have reasonable aspect ratio
                aspect_ratio = ew / eh if eh > 0 else 0
                if 0.8 < aspect_ratio < 2.5:
                    valid_eyes.append((ex, ey, ew, eh))

        return valid_eyes

    def _draw_eyes(self, frame: np.ndarray, face_x: int, face_y: int,
                   eyes: List[Tuple], max_eyes: int = 2):
        """Draw eye indicators on frame"""
        for (ex, ey, ew, eh) in eyes[:max_eyes]:
            # Draw circle at eye center
            cv2.circle(frame,
                      (face_x + ex + ew // 2, face_y + ey + eh // 2),
                      5, (255, 0, 0), -1)
            # Draw rectangle around eye
            cv2.rectangle(frame,
                         (face_x + ex, face_y + ey),
                         (face_x + ex + ew, face_y + ey + eh),
                         (255, 0, 0), 1)

    def update_parameters(self, **kwargs):
        """Update detection parameters dynamically"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.info(f"Updated {key} to {value}")
            else:
                logger.warning(f"Unknown parameter: {key}")
