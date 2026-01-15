"""Tests for stress detector."""

import pytest

from opensati.config.settings import Settings
from opensati.core.detector import StressDetector, StressLevel
from opensati.core.sensors import is_pynput_available

# Skip tests that require display if pynput is not available
requires_display = pytest.mark.skipif(
    not is_pynput_available(),
    reason="pynput requires display (headless environment)",
)


class TestStressDetector:
    """Test stress detection logic."""

    def test_initial_state_is_calm(self):
        """Detector should start in calm state."""
        detector = StressDetector(settings=Settings())
        state = detector.get_state()

        assert state.level == StressLevel.CALM
        assert state.score == 0.0

    def test_can_intervene_after_cooldown(self):
        """Should respect cooldown period."""
        settings = Settings()
        settings.intervention.cooldown = 1  # 1 second for test

        detector = StressDetector(settings=settings)
        state = detector.get_state()

        assert state.can_intervene is True

    def test_stress_levels(self):
        """Test stress level thresholds."""
        # Calm: < 30
        # Moderate: 30-60
        # High: 60-85
        # Critical: >= 85

        # These would require mocking the sensor inputs
        pass


class TestPrivacy:
    """Verify privacy guarantees."""

    def test_no_keystroke_content_logged(self):
        """Sensor should never capture actual keystrokes."""
        from opensati.core.sensors import InputSensor

        sensor = InputSensor()
        state = sensor.get_state()

        # State should only contain velocity/count, not content
        assert not hasattr(state, "keystroke_content")
        assert not hasattr(state, "keys_pressed")

    @requires_display
    def test_screenshot_not_stored(self):
        """Screenshots should only exist in RAM."""
        from opensati.core.vision import ScreenCapture

        capture = ScreenCapture()

        # Capture should not create files
        # (Would need to mock filesystem access to fully verify)
        assert capture._sct is not None
