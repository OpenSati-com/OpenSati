"""Multi-modal stress detector combining all sensor inputs."""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

from opensati.config.settings import Settings, get_settings
from opensati.core.sensors import InputSensor


class StressLevel(Enum):
    """Stress level categories."""

    CALM = "calm"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DetectorState:
    """Current detector state."""

    level: StressLevel = StressLevel.CALM
    score: float = 0.0
    input_score: float = 0.0
    breathing_score: float = 0.0
    posture_score: float = 0.0
    last_intervention: float = 0.0
    can_intervene: bool = True


@dataclass
class StressDetector:
    """
    Combines multiple sensor inputs to detect stress.

    Fusion algorithm:
    - Input velocity (keyboard/mouse) = 50% weight
    - Breathing rate (if enabled) = 30% weight
    - Posture (if enabled) = 20% weight
    """

    settings: Settings = field(default_factory=get_settings)

    # Callbacks
    on_stress_detected: Callable[[StressLevel, float], None] | None = None
    on_calm_restored: Callable[[], None] | None = None

    # Internal state
    _input_sensor: InputSensor | None = None
    _last_intervention_time: float = 0.0
    _current_level: StressLevel = StressLevel.CALM

    def __post_init__(self) -> None:
        """Initialize sensors based on settings."""
        if self.settings.sensors.keyboard or self.settings.sensors.mouse:
            self._input_sensor = InputSensor(
                window_size=10.0,
                baseline_duration=self.settings.detection.baseline_window,
                stress_threshold=self.settings.detection.stress_threshold,
            )

    def start(self) -> None:
        """Start all enabled sensors."""
        if self._input_sensor:
            self._input_sensor.start()

        print("🧠 Stress detector started")

    def stop(self) -> None:
        """Stop all sensors."""
        if self._input_sensor:
            self._input_sensor.stop()

        print("🧠 Stress detector stopped")

    def get_state(self) -> DetectorState:
        """Get current detector state."""
        now = time.time()
        cooldown = self.settings.intervention.cooldown
        can_intervene = (now - self._last_intervention_time) > cooldown

        # Get input sensor state
        input_score = 0.0
        if self._input_sensor:
            sensor_state = self._input_sensor.get_state()
            input_score = sensor_state.current_stress_score

        # Placeholder for other sensors (breathing, posture)
        # These would be integrated when those modules are enabled
        breathing_score = 0.0
        posture_score = 0.0

        # Weighted fusion
        total_score = input_score * 0.5 + breathing_score * 0.3 + posture_score * 0.2

        # Determine level
        if total_score < 30:
            level = StressLevel.CALM
        elif total_score < 60:
            level = StressLevel.MODERATE
        elif total_score < 85:
            level = StressLevel.HIGH
        else:
            level = StressLevel.CRITICAL

        return DetectorState(
            level=level,
            score=total_score,
            input_score=input_score,
            breathing_score=breathing_score,
            posture_score=posture_score,
            last_intervention=self._last_intervention_time,
            can_intervene=can_intervene,
        )

    def check_and_intervene(self) -> bool:
        """
        Check stress levels and trigger intervention if needed.

        Returns True if intervention was triggered.
        """
        state = self.get_state()

        # Track state changes
        previous_level = self._current_level
        self._current_level = state.level

        # Callback for calm restored
        if previous_level in (StressLevel.HIGH, StressLevel.CRITICAL):
            if state.level == StressLevel.CALM and self.on_calm_restored:
                self.on_calm_restored()

        # Check if intervention is needed and allowed
        if state.level in (StressLevel.HIGH, StressLevel.CRITICAL):
            if state.can_intervene:
                self._last_intervention_time = time.time()
                if self.on_stress_detected:
                    self.on_stress_detected(state.level, state.score)
                return True

        return False
