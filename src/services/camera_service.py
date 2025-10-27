"""
Camera Service
Handles camera capture and integrates with face detection
"""

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
import logging
from services.face_detector import FaceDetector, FaceDetectionResult

logger = logging.getLogger(__name__)


class CameraService(QThread):
    """
    Thread-safe camera service that captures frames and performs face detection
    """
    frame_ready = pyqtSignal(np.ndarray)
    face_status = pyqtSignal(object)  # Emits FaceDetectionResult
    error_occurred = pyqtSignal(str)

    def __init__(self, camera_index: int = 0, fps: int = 30):
        """
        Initialize camera service

        Args:
            camera_index: Index of camera device
            fps: Target frames per second
        """
        super().__init__()
        self.camera_index = camera_index
        self.fps = fps
        self.running = False
        self.face_detector = FaceDetector()
        self._camera = None

    def run(self):
        """Main camera loop"""
        try:
            self._camera = cv2.VideoCapture(self.camera_index)

            if not self._camera.isOpened():
                error_msg = f"Failed to open camera at index {self.camera_index}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return

            # Set camera properties
            self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self._camera.set(cv2.CAP_PROP_FPS, self.fps)

            logger.info(f"Camera started successfully (index: {self.camera_index})")
            self.running = True

            while self.running:
                ret, frame = self._camera.read()

                if not ret:
                    logger.warning("Failed to read frame from camera")
                    continue

                # Mirror the frame for more natural interaction
                frame = cv2.flip(frame, 1)

                # Perform face detection
                result, annotated_frame = self.face_detector.detect(frame)

                # Emit signals
                self.face_status.emit(result)
                self.frame_ready.emit(annotated_frame)

        except Exception as e:
            error_msg = f"Camera error: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

        finally:
            self._cleanup()

    def stop(self):
        """Stop the camera service"""
        logger.info("Stopping camera service...")
        self.running = False
        self.wait()

    def _cleanup(self):
        """Clean up camera resources"""
        if self._camera is not None:
            self._camera.release()
            self._camera = None
            logger.info("Camera released")

    def update_detector_parameters(self, **kwargs):
        """Update face detector parameters"""
        self.face_detector.update_parameters(**kwargs)
