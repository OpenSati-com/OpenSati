"""Tests for sensor modules."""

import time

from opensati.core.sensors import InputSensor, SensorState


class TestInputSensor:
    """Test input sensor functionality."""

    def test_initial_state(self):
        """Sensor should start with zero values."""
        sensor = InputSensor()
        state = sensor.get_state()

        assert state.keystrokes_per_second == 0.0
        assert state.current_stress_score == 0.0
        assert state.is_calibrating is True

    def test_state_structure(self):
        """Sensor state should have expected fields."""
        state = SensorState()

        # Check all fields exist
        assert hasattr(state, "keystrokes_per_second")
        assert hasattr(state, "mouse_clicks_per_second")
        assert hasattr(state, "mouse_distance_per_second")
        assert hasattr(state, "current_stress_score")
        assert hasattr(state, "baseline_typing_speed")
        assert hasattr(state, "is_calibrating")

    def test_no_content_logging(self):
        """Sensor must never expose keystroke content."""
        sensor = InputSensor()

        # Check no content fields exist
        state = sensor.get_state()
        assert not hasattr(state, "keystroke_content")
        assert not hasattr(state, "keys_pressed")
        assert not hasattr(state, "key_buffer")
        assert not hasattr(state, "text")

    def test_start_stop(self):
        """Sensor should start and stop cleanly."""
        sensor = InputSensor()

        sensor.start()
        assert sensor._running is True

        sensor.stop()
        assert sensor._running is False


class TestPrivacyGuarantees:
    """Verify privacy is enforced at the sensor level."""

    def test_input_sensor_velocity_only(self):
        """Input sensor should only track velocity, not content."""
        sensor = InputSensor()

        # Internal state should not store keys
        assert not hasattr(sensor, "_key_buffer")
        assert not hasattr(sensor, "_keystroke_content")

        # Only timing should be stored
        assert hasattr(sensor, "_keystroke_times")
