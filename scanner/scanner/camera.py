"""Camera capture module for dual USB Arducam cameras."""

import cv2
import logging
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import base64

logger = logging.getLogger(__name__)


@dataclass
class CameraInfo:
    """Information about a detected camera."""
    device_id: int
    name: str
    position: str  # "left" or "right"


@dataclass
class CaptureResult:
    """Result of a capture operation."""
    success: bool
    left_image: Optional[bytes] = None
    right_image: Optional[bytes] = None
    error: Optional[str] = None


class Camera:
    """Controls a single USB camera."""

    def __init__(self, device_id: int, position: str):
        self.device_id = device_id
        self.position = position
        self.cap: Optional[cv2.VideoCapture] = None
        self._lock = threading.Lock()

    def open(self) -> bool:
        """Open the camera device."""
        with self._lock:
            if self.cap is not None:
                return True

            self.cap = cv2.VideoCapture(self.device_id)
            if not self.cap.isOpened():
                logger.error(f"Failed to open camera {self.device_id}")
                self.cap = None
                return False

            # Configure for high resolution capture
            # Arducam 16MP: 4656x3496 max, but we'll use a reasonable capture size
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4656)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 3496)

            # Get actual resolution (camera may not support requested)
            actual_w = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_h = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            logger.info(f"Camera {self.position} opened at {actual_w}x{actual_h}")

            return True

    def close(self):
        """Close the camera device."""
        with self._lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None

    def capture(self, quality: int = 95) -> Optional[bytes]:
        """Capture a single frame and return as JPEG bytes."""
        with self._lock:
            if self.cap is None:
                logger.error(f"Camera {self.position} not open")
                return None

            # Grab a few frames to ensure we get a fresh one (not buffered)
            for _ in range(3):
                self.cap.grab()

            ret, frame = self.cap.read()
            if not ret:
                logger.error(f"Failed to capture from camera {self.position}")
                return None

            # Encode as JPEG
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
            success, buffer = cv2.imencode('.jpg', frame, encode_params)
            if not success:
                logger.error(f"Failed to encode JPEG from camera {self.position}")
                return None

            return buffer.tobytes()

    def get_preview_frame(self, max_width: int = 400) -> Optional[str]:
        """Get a preview frame as base64-encoded JPEG for web display."""
        with self._lock:
            if self.cap is None:
                return None

            ret, frame = self.cap.read()
            if not ret:
                return None

            # Resize for preview
            h, w = frame.shape[:2]
            scale = max_width / w
            new_size = (max_width, int(h * scale))
            preview = cv2.resize(frame, new_size)

            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', preview, [cv2.IMWRITE_JPEG_QUALITY, 70])
            return base64.b64encode(buffer).decode('utf-8')

    @property
    def is_open(self) -> bool:
        return self.cap is not None and self.cap.isOpened()


class DualCameraController:
    """Controls the dual-camera setup for book scanning."""

    def __init__(self):
        self.left: Optional[Camera] = None
        self.right: Optional[Camera] = None
        self.page_number: int = 0
        self._lock = threading.Lock()

    def detect_cameras(self) -> list[CameraInfo]:
        """Detect available USB cameras."""
        cameras = []

        # Check first 10 video devices
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Try to get camera name
                backend = cap.getBackendName()
                cameras.append(CameraInfo(
                    device_id=i,
                    name=f"Camera {i} ({backend})",
                    position="unassigned"
                ))
                cap.release()

        logger.info(f"Detected {len(cameras)} cameras")
        return cameras

    def configure(self, left_device: int, right_device: int) -> bool:
        """Configure the dual camera setup."""
        with self._lock:
            # Close existing cameras
            if self.left:
                self.left.close()
            if self.right:
                self.right.close()

            self.left = Camera(left_device, "left")
            self.right = Camera(right_device, "right")

            left_ok = self.left.open()
            right_ok = self.right.open()

            if not left_ok or not right_ok:
                logger.error("Failed to open one or both cameras")
                return False

            logger.info(f"Cameras configured: left={left_device}, right={right_device}")
            return True

    def swap_cameras(self):
        """Swap left and right camera assignments."""
        with self._lock:
            if self.left and self.right:
                self.left, self.right = self.right, self.left
                self.left.position = "left"
                self.right.position = "right"
                logger.info("Cameras swapped")

    def capture(self) -> CaptureResult:
        """Capture from both cameras simultaneously."""
        with self._lock:
            if not self.left or not self.right:
                return CaptureResult(success=False, error="Cameras not configured")

            if not self.left.is_open or not self.right.is_open:
                return CaptureResult(success=False, error="Cameras not open")

            # Capture from both (could parallelize with threads if needed)
            left_img = self.left.capture()
            right_img = self.right.capture()

            if left_img is None or right_img is None:
                return CaptureResult(
                    success=False,
                    error="Capture failed",
                    left_image=left_img,
                    right_image=right_img
                )

            self.page_number += 2

            return CaptureResult(
                success=True,
                left_image=left_img,
                right_image=right_img
            )

    def get_previews(self) -> tuple[Optional[str], Optional[str]]:
        """Get preview frames from both cameras as base64 JPEG."""
        left_preview = self.left.get_preview_frame() if self.left else None
        right_preview = self.right.get_preview_frame() if self.right else None
        return left_preview, right_preview

    def close(self):
        """Close all cameras."""
        with self._lock:
            if self.left:
                self.left.close()
            if self.right:
                self.right.close()

    @property
    def is_ready(self) -> bool:
        """Check if both cameras are ready."""
        return (
            self.left is not None and
            self.right is not None and
            self.left.is_open and
            self.right.is_open
        )
