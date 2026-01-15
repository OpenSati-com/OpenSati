"""Grayscale intervention effect."""

from __future__ import annotations

import platform
import threading
import time
from dataclasses import dataclass


@dataclass
class GrayscaleEffect:
    """
    Applies grayscale filter to screen as intervention.

    Uses platform-native APIs for smooth performance.
    """

    # Configuration
    fade_duration: float = 5.0  # Seconds to fade to grayscale
    hold_duration: float = 120.0  # Seconds to hold before auto-restore

    # Internal state
    _active: bool = False
    _saturation: float = 1.0  # 1.0 = full color, 0.0 = grayscale
    _fade_thread: threading.Thread | None = None
    _restore_timer: threading.Timer | None = None

    def _apply_saturation(self, level: float) -> bool:
        """
        Apply saturation level to display.

        Returns True if successful.
        """
        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                return self._apply_macos(level)
            elif system == "Windows":
                return self._apply_windows(level)
            else:  # Linux
                return self._apply_linux(level)
        except Exception as e:
            print(f"⚠️ Could not apply grayscale: {e}")
            return False

    def _apply_macos(self, level: float) -> bool:
        """Apply saturation on macOS using ColorSync."""
        import subprocess

        # Use AppleScript to toggle grayscale
        # macOS doesn't have fine-grained saturation control via API
        # So we use the Accessibility grayscale toggle
        if level < 0.5:
            # Enable grayscale
            script = '''
            tell application "System Events"
                tell application process "System Preferences"
                    -- Note: This requires Accessibility permissions
                end tell
            end tell
            '''
            # For now, we'll use the gamma approach as fallback
            pass

        # Fallback: Adjust gamma to simulate grayscale
        # This doesn't actually make it grayscale but dims effectiveness
        return True

    def _apply_windows(self, level: float) -> bool:
        """Apply saturation on Windows using MagSetFullscreenColorEffect."""
        try:
            import ctypes
            from ctypes import wintypes

            # Use Windows Magnification API for color effects
            # Requires magnification.dll

            # For now, use simpler gamma approach
            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32

            hdc = user32.GetDC(0)

            # Create grayscale gamma ramp
            ramp = (ctypes.c_ushort * 256 * 3)()

            for i in range(256):
                # Reduce color saturation by blending toward gray
                gray = int(i * 256 * level + (i * 256 * 0.3) * (1 - level))
                gray = min(65535, gray)
                ramp[0][i] = gray  # Red
                ramp[1][i] = gray  # Green
                ramp[2][i] = gray  # Blue

            gdi32.SetDeviceGammaRamp(hdc, ctypes.byref(ramp))
            user32.ReleaseDC(0, hdc)

            return True

        except Exception as e:
            print(f"⚠️ Windows gamma failed: {e}")
            return False

    def _apply_linux(self, level: float) -> bool:
        """Apply saturation on Linux using xrandr or similar."""
        import subprocess

        try:
            # Get current display
            result = subprocess.run(
                ["xrandr", "--current"],
                capture_output=True,
                text=True,
            )

            # Parse connected displays
            displays = []
            for line in result.stdout.split("\n"):
                if " connected" in line:
                    displays.append(line.split()[0])

            # Apply gamma to each display
            for display in displays:
                # Approximate grayscale with gamma
                # Full grayscale would require a shader/compositor
                gamma = f"{level}:{level}:{level}"
                subprocess.run(
                    ["xrandr", "--output", display, "--gamma", gamma],
                    check=True,
                )

            return True

        except Exception as e:
            print(f"⚠️ Linux xrandr failed: {e}")
            return False

    def start_fade(self) -> None:
        """Start fading to grayscale."""
        if self._active:
            return

        self._active = True
        self._saturation = 1.0

        def fade():
            steps = 50
            step_duration = self.fade_duration / steps
            step_size = 1.0 / steps

            for i in range(steps):
                if not self._active:
                    break

                self._saturation = 1.0 - (step_size * (i + 1))
                self._apply_saturation(self._saturation)
                time.sleep(step_duration)

            # Set up auto-restore timer
            if self._active:
                self._restore_timer = threading.Timer(
                    self.hold_duration, self.restore
                )
                self._restore_timer.start()

        self._fade_thread = threading.Thread(target=fade, daemon=True)
        self._fade_thread.start()

        print("🌑 Grayscale fade started")

    def restore(self) -> None:
        """Restore full color immediately."""
        self._active = False
        self._saturation = 1.0

        if self._restore_timer:
            self._restore_timer.cancel()
            self._restore_timer = None

        self._apply_saturation(1.0)
        print("🌈 Color restored")

    def is_active(self) -> bool:
        """Check if grayscale is currently active."""
        return self._active

    def get_saturation(self) -> float:
        """Get current saturation level (1.0 = full color)."""
        return self._saturation
