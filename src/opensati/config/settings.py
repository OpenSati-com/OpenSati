"""Configuration management for OpenSati."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


def get_config_path() -> Path:
    """Get the path to config.yaml, checking multiple locations."""
    # Check current directory first
    local_config = Path("config.yaml")
    if local_config.exists():
        return local_config

    # Check user's home directory
    home_config = Path.home() / ".opensati" / "config.yaml"
    if home_config.exists():
        return home_config

    # Check package directory
    package_dir = Path(__file__).parent.parent.parent.parent
    package_config = package_dir / "config.yaml"
    if package_config.exists():
        return package_config

    # Return default (will create if needed)
    return local_config


@dataclass
class SensorConfig:
    """Configuration for sensor modules."""

    keyboard: bool = True
    mouse: bool = True
    screen: bool = False
    webcam: bool = False
    microphone: bool = False


@dataclass
class DetectionConfig:
    """Configuration for stress detection."""

    stress_threshold: int = 50
    velocity_multiplier: float = 1.3
    tab_switch_limit: int = 40
    baseline_window: int = 1800


@dataclass
class BreathingConfig:
    """Configuration for breathing analysis."""

    min_rate: int = 8
    max_rate: int = 20
    analysis_window: int = 60


@dataclass
class PostureConfig:
    """Configuration for posture detection."""

    neck_angle_threshold: int = 15
    check_interval: int = 10
    blur_intensity: float = 0.7


@dataclass
class IntentConfig:
    """Configuration for intent-reality checking."""

    check_interval: int = 30
    mismatch_threshold: int = 2


@dataclass
class InterventionConfig:
    """Configuration for interventions."""

    style: str = "grayscale"  # grayscale, blur, notification
    fade_duration: int = 5
    recovery_method: str = "breath"  # breath, timeout, manual
    cooldown: int = 120


@dataclass
class AIConfig:
    """Configuration for local AI."""

    model: str = "llama3"
    vision_model: str = "llava"
    timeout: int = 10


@dataclass
class MeetingConfig:
    """Configuration for meeting detection."""

    apps: list[str] = field(
        default_factory=lambda: [
            "zoom.us",
            "Microsoft Teams",
            "Slack",
            "Google Meet",
            "FaceTime",
        ]
    )
    decompression_duration: int = 60


@dataclass
class PrivacyConfig:
    """Privacy settings (read-only enforced)."""

    log_content: bool = False
    screenshot_retention: int = 0
    network_requests: int = 0


@dataclass
class Settings:
    """Main settings container."""

    sensors: SensorConfig = field(default_factory=SensorConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    breathing: BreathingConfig = field(default_factory=BreathingConfig)
    posture: PostureConfig = field(default_factory=PostureConfig)
    intent: IntentConfig = field(default_factory=IntentConfig)
    intervention: InterventionConfig = field(default_factory=InterventionConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    meeting: MeetingConfig = field(default_factory=MeetingConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)

    @classmethod
    def load(cls, path: Path | None = None) -> Settings:
        """Load settings from YAML file."""
        if path is None:
            path = get_config_path()

        settings = cls()

        if not path.exists():
            return settings

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}

            # Update each section if present
            if "sensors" in data:
                settings.sensors = SensorConfig(**data["sensors"])
            if "detection" in data:
                settings.detection = DetectionConfig(**data["detection"])
            if "breathing" in data:
                settings.breathing = BreathingConfig(**data["breathing"])
            if "posture" in data:
                settings.posture = PostureConfig(**data["posture"])
            if "intent" in data:
                settings.intent = IntentConfig(**data["intent"])
            if "intervention" in data:
                settings.intervention = InterventionConfig(**data["intervention"])
            if "ai" in data:
                settings.ai = AIConfig(**data["ai"])
            if "meeting" in data:
                meeting_data = data["meeting"]
                # Handle 'apps' key which might be in root of meeting section
                settings.meeting = MeetingConfig(
                    apps=meeting_data.get("apps", MeetingConfig().apps),
                    decompression_duration=meeting_data.get(
                        "decompression_duration", 60
                    ),
                )

        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")

        return settings

    def save(self, path: Path | None = None) -> None:
        """Save settings to YAML file."""
        if path is None:
            path = get_config_path()

        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "sensors": {
                "keyboard": self.sensors.keyboard,
                "mouse": self.sensors.mouse,
                "screen": self.sensors.screen,
                "webcam": self.sensors.webcam,
                "microphone": self.sensors.microphone,
            },
            "detection": {
                "stress_threshold": self.detection.stress_threshold,
                "velocity_multiplier": self.detection.velocity_multiplier,
                "tab_switch_limit": self.detection.tab_switch_limit,
                "baseline_window": self.detection.baseline_window,
            },
            "intervention": {
                "style": self.intervention.style,
                "fade_duration": self.intervention.fade_duration,
                "recovery_method": self.intervention.recovery_method,
                "cooldown": self.intervention.cooldown,
            },
            "ai": {
                "model": self.ai.model,
                "vision_model": self.ai.vision_model,
                "timeout": self.ai.timeout,
            },
        }

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or load the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def reload_settings() -> Settings:
    """Force reload settings from disk."""
    global _settings
    _settings = Settings.load()
    return _settings
