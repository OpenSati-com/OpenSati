"""Intent-Reality checker using Vision-Language Model."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable

from opensati.ai.ollama_client import OllamaClient
from opensati.config.settings import get_settings
from opensati.core.vision import ScreenCapture


@dataclass
class IntentState:
    """Current intent checking state."""

    current_intent: str = ""
    last_check_time: float = 0.0
    last_match: bool = True
    last_explanation: str = ""
    mismatch_duration: float = 0.0
    is_enabled: bool = False


@dataclass
class IntentChecker:
    """
    Checks if screen content matches user's stated intent.

    Privacy:
    - Screenshots processed locally via Ollama VLM
    - Images processed in RAM only, never stored
    - Only match/mismatch logged, not content
    """

    # Configuration
    check_interval: float = 30.0  # Seconds between checks
    mismatch_threshold: float = 120.0  # Seconds off-task before intervention

    # Callbacks
    on_mismatch_detected: Callable[[str, str], None] | None = None

    # Internal state
    _current_intent: str = ""
    _screen_capture: ScreenCapture | None = None
    _ollama: OllamaClient | None = None
    _last_check: float = 0.0
    _mismatch_start: float | None = None
    _last_explanation: str = ""
    _running: bool = False

    def __post_init__(self) -> None:
        """Initialize components."""
        settings = get_settings()
        self.check_interval = settings.intent.check_interval
        self.mismatch_threshold = settings.intent.mismatch_threshold * 60  # Convert to seconds

        self._screen_capture = ScreenCapture()
        self._ollama = OllamaClient()

    def set_intent(self, intent: str) -> None:
        """Set the user's current work intent."""
        self._current_intent = intent.strip()
        self._mismatch_start = None
        self._last_explanation = ""
        print(f"🎯 Intent set: {self._current_intent}")

    def clear_intent(self) -> None:
        """Clear the current intent (disable checking)."""
        self._current_intent = ""
        self._mismatch_start = None
        print("🎯 Intent cleared")

    def start(self) -> bool:
        """Start intent checking."""
        if not self._ollama.is_available():
            print("⚠️ Intent checker requires Ollama. Install and run Ollama first.")
            return False

        self._running = True
        print("🎯 Intent checker started")
        return True

    def stop(self) -> None:
        """Stop intent checking."""
        self._running = False
        print("🎯 Intent checker stopped")

    def check(self) -> IntentState:
        """
        Check if current screen matches intent.

        Returns current state.
        """
        if not self._running or not self._current_intent:
            return IntentState(is_enabled=False)

        now = time.time()

        # Check if enough time has passed
        if now - self._last_check < self.check_interval:
            mismatch_duration = 0.0
            if self._mismatch_start:
                mismatch_duration = now - self._mismatch_start

            return IntentState(
                current_intent=self._current_intent,
                last_check_time=self._last_check,
                last_match=self._mismatch_start is None,
                last_explanation=self._last_explanation,
                mismatch_duration=mismatch_duration,
                is_enabled=True,
            )

        self._last_check = now

        # Capture screen
        self._screen_capture.capture()
        image_bytes = self._screen_capture.get_for_ai()

        if not image_bytes:
            return IntentState(
                current_intent=self._current_intent,
                is_enabled=True,
            )

        # Check with AI
        matches, explanation = self._ollama.check_intent_match(
            self._current_intent, image_bytes
        )

        # Clear screenshot from memory
        self._screen_capture.clear()

        self._last_explanation = explanation

        # Track mismatch duration
        if matches:
            self._mismatch_start = None
        else:
            if self._mismatch_start is None:
                self._mismatch_start = now
            else:
                # Check if threshold exceeded
                mismatch_duration = now - self._mismatch_start
                if mismatch_duration >= self.mismatch_threshold:
                    if self.on_mismatch_detected:
                        self.on_mismatch_detected(self._current_intent, explanation)

        mismatch_duration = 0.0
        if self._mismatch_start:
            mismatch_duration = now - self._mismatch_start

        return IntentState(
            current_intent=self._current_intent,
            last_check_time=now,
            last_match=matches,
            last_explanation=explanation,
            mismatch_duration=mismatch_duration,
            is_enabled=True,
        )

    def get_state(self) -> IntentState:
        """Get current intent state without triggering a check."""
        if not self._current_intent:
            return IntentState(is_enabled=False)

        mismatch_duration = 0.0
        if self._mismatch_start:
            mismatch_duration = time.time() - self._mismatch_start

        return IntentState(
            current_intent=self._current_intent,
            last_check_time=self._last_check,
            last_match=self._mismatch_start is None,
            last_explanation=self._last_explanation,
            mismatch_duration=mismatch_duration,
            is_enabled=True,
        )
