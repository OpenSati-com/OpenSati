"""Keyboard and mouse sensor for detecting typing patterns and stress."""

from __future__ import annotations

import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field

from pynput import keyboard, mouse


@dataclass
class SensorState:
    """Current state of input sensors."""

    keystrokes_per_second: float = 0.0
    mouse_clicks_per_second: float = 0.0
    mouse_distance_per_second: float = 0.0
    current_stress_score: float = 0.0
    baseline_typing_speed: float = 0.0
    is_calibrating: bool = True


@dataclass
class InputSensor:
    """
    Monitors keyboard and mouse input patterns.

    Privacy: Only captures velocity/frequency, NEVER keystroke content.
    """

    # Configuration
    window_size: float = 10.0  # Seconds to track
    baseline_duration: float = 300.0  # 5 minutes to establish baseline
    stress_threshold: float = 50.0  # Keystrokes per window to trigger

    # Callbacks
    on_stress_detected: Callable[[float], None] | None = None

    # Internal state
    _keystroke_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    _click_times: deque = field(default_factory=lambda: deque(maxlen=500))
    _mouse_positions: deque = field(default_factory=lambda: deque(maxlen=100))
    _baseline_samples: list = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _running: bool = False
    _keyboard_listener: keyboard.Listener | None = None
    _mouse_listener: mouse.Listener | None = None
    _start_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize deques after dataclass init."""
        self._keystroke_times = deque(maxlen=1000)
        self._click_times = deque(maxlen=500)
        self._mouse_positions = deque(maxlen=100)
        self._baseline_samples = []
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start monitoring keyboard and mouse."""
        if self._running:
            return

        self._running = True
        self._start_time = time.time()

        # Start keyboard listener (captures timing only, NOT keys)
        self._keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self._keyboard_listener.start()

        # Start mouse listener
        self._mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click, on_move=self._on_mouse_move
        )
        self._mouse_listener.start()

        print("🎹 Input sensors started (velocity only - no content logging)")

    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False

        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None

        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None

        print("🎹 Input sensors stopped")

    def _on_key_press(self, key) -> None:
        """Record keystroke timing (NOT the actual key)."""
        with self._lock:
            self._keystroke_times.append(time.time())

    def _on_mouse_click(self, x: int, y: int, button, pressed: bool) -> None:
        """Record mouse click timing."""
        if pressed:
            with self._lock:
                self._click_times.append(time.time())

    def _on_mouse_move(self, x: int, y: int) -> None:
        """Record mouse position for velocity calculation."""
        with self._lock:
            self._mouse_positions.append((time.time(), x, y))

    def get_state(self) -> SensorState:
        """Get current sensor state."""
        now = time.time()
        window_start = now - self.window_size
        is_calibrating = (now - self._start_time) < self.baseline_duration

        with self._lock:
            # Count keystrokes in window
            recent_keystrokes = sum(
                1 for t in self._keystroke_times if t > window_start
            )
            keystrokes_per_second = recent_keystrokes / self.window_size

            # Count clicks in window
            recent_clicks = sum(1 for t in self._click_times if t > window_start)
            clicks_per_second = recent_clicks / self.window_size

            # Calculate mouse velocity
            mouse_distance = 0.0
            recent_positions = [
                (t, x, y) for t, x, y in self._mouse_positions if t > window_start
            ]
            for i in range(1, len(recent_positions)):
                _, x1, y1 = recent_positions[i - 1]
                _, x2, y2 = recent_positions[i]
                mouse_distance += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            mouse_velocity = mouse_distance / self.window_size

            # Update baseline during calibration
            if is_calibrating and recent_keystrokes > 0:
                self._baseline_samples.append(keystrokes_per_second)

            # Calculate baseline
            baseline = 0.0
            if self._baseline_samples:
                baseline = sum(self._baseline_samples) / len(self._baseline_samples)

            # Calculate stress score (0-100)
            stress_score = min(100, (recent_keystrokes / self.stress_threshold) * 100)

        return SensorState(
            keystrokes_per_second=keystrokes_per_second,
            mouse_clicks_per_second=clicks_per_second,
            mouse_distance_per_second=mouse_velocity,
            current_stress_score=stress_score,
            baseline_typing_speed=baseline,
            is_calibrating=is_calibrating,
        )

    def check_stress(self) -> float | None:
        """
        Check if stress threshold exceeded.

        Returns stress score if triggered, None otherwise.
        """
        state = self.get_state()

        # Don't trigger during calibration
        if state.is_calibrating:
            return None

        # Check against threshold
        if state.current_stress_score >= 100:
            if self.on_stress_detected:
                self.on_stress_detected(state.current_stress_score)
            return state.current_stress_score

        return None
