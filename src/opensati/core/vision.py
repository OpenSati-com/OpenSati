"""Vision processing for screen capture and webcam posture detection."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from io import BytesIO
from typing import Callable

import cv2
import mss
import numpy as np
from PIL import Image


@dataclass
class ScreenState:
    """Current screen analysis state."""

    brightness: float = 0.0
    has_screenshot: bool = False


@dataclass
class PostureState:
    """Current posture analysis state."""

    neck_angle: float = 0.0
    is_good_posture: bool = True
    face_detected: bool = False
    is_enabled: bool = False


@dataclass
class ScreenCapture:
    """
    Captures screen for AI analysis.

    Privacy:
    - Screenshots processed in RAM only
    - NEVER saved to disk
    - Immediately deleted after AI processing
    """

    # Configuration
    capture_interval: float = 30.0  # Seconds between captures
    scale_factor: float = 0.25  # Downscale for efficiency

    # Internal state
    _sct: mss.mss | None = None
    _last_capture: np.ndarray | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def __post_init__(self) -> None:
        """Initialize screen capture."""
        self._sct = mss.mss()
        self._lock = threading.Lock()

    def capture(self) -> np.ndarray | None:
        """
        Capture current screen.

        Returns numpy array (RGB), or None on failure.
        Screenshot is stored ONLY in RAM.
        """
        try:
            # Capture primary monitor
            monitor = self._sct.monitors[1]
            screenshot = self._sct.grab(monitor)

            # Convert to numpy array
            img = np.array(screenshot)

            # Convert BGRA to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

            # Downscale for efficiency
            if self.scale_factor < 1.0:
                new_size = (
                    int(img.shape[1] * self.scale_factor),
                    int(img.shape[0] * self.scale_factor),
                )
                img = cv2.resize(img, new_size)

            with self._lock:
                self._last_capture = img

            return img

        except Exception as e:
            print(f"⚠️ Screen capture failed: {e}")
            return None

    def get_for_ai(self) -> bytes | None:
        """
        Get screenshot as JPEG bytes for AI analysis.

        Returns JPEG bytes suitable for VLM, or None.
        """
        with self._lock:
            if self._last_capture is None:
                return None

            img = self._last_capture.copy()

        # Convert to PIL and then to JPEG bytes
        pil_img = Image.fromarray(img)
        buffer = BytesIO()
        pil_img.save(buffer, format="JPEG", quality=60)
        return buffer.getvalue()

    def get_state(self) -> ScreenState:
        """Get current screen state."""
        with self._lock:
            if self._last_capture is None:
                return ScreenState()

            # Calculate average brightness
            gray = cv2.cvtColor(self._last_capture, cv2.COLOR_RGB2GRAY)
            brightness = float(np.mean(gray))

        return ScreenState(brightness=brightness, has_screenshot=True)

    def clear(self) -> None:
        """Clear cached screenshot from memory."""
        with self._lock:
            self._last_capture = None


@dataclass
class PostureDetector:
    """
    Detects posture via webcam.

    Privacy:
    - Video processed in real-time, NEVER stored
    - Only posture metrics logged, not images
    - Requires explicit user opt-in
    """

    # Configuration
    neck_angle_threshold: int = 15  # Degrees forward = "tech neck"
    check_interval: float = 10.0  # Seconds between checks
    camera_index: int = 0

    # Callbacks
    on_bad_posture: Callable[[float], None] | None = None
    on_posture_corrected: Callable[[], None] | None = None

    # Internal state
    _running: bool = False
    _capture: cv2.VideoCapture | None = None
    _face_cascade: cv2.CascadeClassifier | None = None
    _last_check: float = 0.0
    _last_angle: float = 0.0
    _was_bad_posture: bool = False

    def start(self) -> bool:
        """
        Start posture monitoring.

        Returns True if started successfully.
        """
        try:
            self._capture = cv2.VideoCapture(self.camera_index)
            if not self._capture.isOpened():
                print("⚠️ Could not open webcam")
                return False

            # Load face detection model
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._face_cascade = cv2.CascadeClassifier(cascade_path)

            self._running = True
            print("📷 Posture detector started (posture only - no images stored)")
            return True

        except Exception as e:
            print(f"⚠️ Could not start posture detection: {e}")
            return False

    def stop(self) -> None:
        """Stop posture monitoring."""
        self._running = False

        if self._capture:
            self._capture.release()
            self._capture = None

        print("📷 Posture detector stopped")

    def _detect_posture(self) -> tuple[float, bool]:
        """
        Detect head position and estimate neck angle.

        Returns (neck_angle, face_detected).
        A positive angle means leaning forward (bad posture).
        """
        if not self._capture or not self._face_cascade:
            return (0.0, False)

        ret, frame = self._capture.read()
        if not ret:
            return (0.0, False)

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = self._face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
        )

        if len(faces) == 0:
            return (0.0, False)

        # Use largest face
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

        # Estimate neck angle from face position
        # If face is in lower third of frame = leaning forward
        frame_height = frame.shape[0]
        face_center_y = y + h / 2

        # Normalize to -1 to 1 (0 = center, positive = lower/forward)
        position_ratio = (face_center_y - frame_height / 2) / (frame_height / 2)

        # Convert to approximate neck angle (rough estimation)
        neck_angle = position_ratio * 30  # Max 30 degrees

        return (neck_angle, True)

    def check_posture(self) -> PostureState:
        """Check current posture."""
        if not self._running:
            return PostureState(is_enabled=False)

        now = time.time()
        if now - self._last_check < self.check_interval:
            return PostureState(
                neck_angle=self._last_angle,
                is_good_posture=self._last_angle < self.neck_angle_threshold,
                face_detected=True,
                is_enabled=True,
            )

        self._last_check = now
        angle, detected = self._detect_posture()
        self._last_angle = angle

        is_bad = angle > self.neck_angle_threshold

        # Callbacks for posture changes
        if is_bad and not self._was_bad_posture:
            if self.on_bad_posture:
                self.on_bad_posture(angle)
        elif not is_bad and self._was_bad_posture:
            if self.on_posture_corrected:
                self.on_posture_corrected()

        self._was_bad_posture = is_bad

        return PostureState(
            neck_angle=angle,
            is_good_posture=not is_bad,
            face_detected=detected,
            is_enabled=True,
        )

    def get_state(self) -> PostureState:
        """Get current posture state."""
        return self.check_posture()
