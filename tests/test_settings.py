"""Tests for configuration management."""

import tempfile
from pathlib import Path

from opensati.config.settings import Settings


class TestSettings:
    """Test settings loading and saving."""

    def test_default_settings(self):
        """Default settings should be sensible."""
        settings = Settings()

        # Sensors default to keyboard/mouse only
        assert settings.sensors.keyboard is True
        assert settings.sensors.mouse is True
        assert settings.sensors.screen is False
        assert settings.sensors.webcam is False
        assert settings.sensors.microphone is False

        # Detection has reasonable threshold
        assert settings.detection.stress_threshold == 50

        # Intervention defaults to grayscale
        assert settings.intervention.style == "grayscale"

    def test_save_and_load(self):
        """Settings should round-trip through YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_config.yaml"

            # Create custom settings
            settings = Settings()
            settings.sensors.screen = True
            settings.detection.stress_threshold = 75
            settings.intervention.style = "blur"

            # Save
            settings.save(path)

            # Load
            loaded = Settings.load(path)

            # Verify
            assert loaded.sensors.screen is True
            assert loaded.detection.stress_threshold == 75
            assert loaded.intervention.style == "blur"


class TestPrivacyDefaults:
    """Verify privacy settings are secure by default."""

    def test_privacy_defaults_are_secure(self):
        """Privacy settings should default to maximum privacy."""
        settings = Settings()

        # High-risk sensors off by default
        assert settings.sensors.screen is False
        assert settings.sensors.webcam is False
        assert settings.sensors.microphone is False

        # Privacy flags should be secure
        assert settings.privacy.log_content is False
        assert settings.privacy.screenshot_retention == 0
        assert settings.privacy.network_requests == 0
