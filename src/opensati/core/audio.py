"""Audio processing for breathing detection."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable

import numpy as np


@dataclass
class BreathingState:
    """Current breathing analysis state."""

    breaths_per_minute: float = 0.0
    is_stressed: bool = False
    is_too_slow: bool = False
    confidence: float = 0.0
    is_enabled: bool = False


@dataclass
class AudioSensor:
    """
    Monitors breathing patterns via microphone.

    Privacy:
    - Audio is analyzed in real-time and NEVER stored
    - Only respiratory rate is logged, not audio content
    - Requires explicit user opt-in
    """

    # Configuration
    min_rate: int = 8  # Breaths per minute (below = concern)
    max_rate: int = 20  # Breaths per minute (above = stressed)
    sample_rate: int = 44100
    chunk_size: int = 1024
    analysis_window: int = 60  # Seconds

    # Callbacks
    on_stress_detected: Callable[[float], None] | None = None
    on_slow_breathing: Callable[[float], None] | None = None

    # Internal state
    _running: bool = False
    _stream = None
    _audio_buffer: list = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _last_rate: float = 0.0

    def __post_init__(self) -> None:
        """Initialize internal state."""
        self._audio_buffer = []
        self._lock = threading.Lock()

    def start(self) -> bool:
        """
        Start audio monitoring.

        Returns True if started successfully, False if PyAudio unavailable.
        """
        try:
            import pyaudio

            self._running = True

            # Initialize PyAudio
            self._pa = pyaudio.PyAudio()
            self._stream = self._pa.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback,
            )
            self._stream.start_stream()

            print("🎤 Audio sensor started (breathing analysis only)")
            return True

        except ImportError:
            print("⚠️ PyAudio not installed. Install with: pip install opensati[audio]")
            return False
        except Exception as e:
            print(f"⚠️ Could not start audio: {e}")
            return False

    def stop(self) -> None:
        """Stop audio monitoring."""
        self._running = False

        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        if hasattr(self, "_pa") and self._pa:
            self._pa.terminate()
            self._pa = None

        print("🎤 Audio sensor stopped")

    def _audio_callback(self, in_data, frame_count, time_info, status) -> tuple:
        """Process incoming audio chunk."""
        import pyaudio

        if not self._running:
            return (None, pyaudio.paComplete)

        # Convert to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)

        with self._lock:
            self._audio_buffer.append(audio_data)

            # Keep only last N seconds
            max_chunks = (self.sample_rate * self.analysis_window) // self.chunk_size
            if len(self._audio_buffer) > max_chunks:
                self._audio_buffer = self._audio_buffer[-max_chunks:]

        return (None, pyaudio.paContinue)

    def _estimate_breathing_rate(self) -> tuple[float, float]:
        """
        Estimate breathing rate from audio envelope.

        Returns (breaths_per_minute, confidence).
        """
        with self._lock:
            if len(self._audio_buffer) < 10:
                return (0.0, 0.0)

            # Concatenate audio
            audio = np.concatenate(self._audio_buffer)

        # Get amplitude envelope (low-pass filtered)
        envelope = np.abs(audio)

        # Downsample for efficiency
        downsample = 100
        envelope = envelope[::downsample]

        if len(envelope) < 100:
            return (0.0, 0.0)

        # Find peaks in envelope (breathing cycles)
        from scipy.signal import find_peaks

        # Expected breathing: 8-20 per minute = 0.13-0.33 Hz
        # With our sample rate and downsampling, peaks should be spaced accordingly
        min_distance = int((self.sample_rate / downsample) * (60 / self.max_rate))
        peaks, properties = find_peaks(envelope, distance=min_distance, prominence=0.01)

        if len(peaks) < 2:
            return (0.0, 0.0)

        # Calculate rate from peak intervals
        intervals = np.diff(peaks)
        avg_interval = np.mean(intervals)
        samples_per_breath = avg_interval * downsample
        seconds_per_breath = samples_per_breath / self.sample_rate
        breaths_per_minute = 60 / seconds_per_breath

        # Confidence based on interval consistency
        interval_std = np.std(intervals) / avg_interval if avg_interval > 0 else 1.0
        confidence = max(0, 1 - interval_std)

        return (breaths_per_minute, confidence)

    def get_state(self) -> BreathingState:
        """Get current breathing state."""
        if not self._running:
            return BreathingState(is_enabled=False)

        try:
            rate, confidence = self._estimate_breathing_rate()
            self._last_rate = rate

            is_stressed = rate > self.max_rate and confidence > 0.5
            is_too_slow = rate < self.min_rate and confidence > 0.5

            return BreathingState(
                breaths_per_minute=rate,
                is_stressed=is_stressed,
                is_too_slow=is_too_slow,
                confidence=confidence,
                is_enabled=True,
            )
        except Exception:
            return BreathingState(is_enabled=True)

    def check_breathing(self) -> float | None:
        """
        Check if breathing indicates stress.

        Returns stress score (0-100) if concerning, None otherwise.
        """
        state = self.get_state()

        if not state.is_enabled or state.confidence < 0.5:
            return None

        if state.is_stressed:
            score = min(100, (state.breaths_per_minute - self.max_rate) / 10 * 100)
            if self.on_stress_detected:
                self.on_stress_detected(state.breaths_per_minute)
            return score

        if state.is_too_slow:
            if self.on_slow_breathing:
                self.on_slow_breathing(state.breaths_per_minute)
            return 50  # Moderate concern

        return None
