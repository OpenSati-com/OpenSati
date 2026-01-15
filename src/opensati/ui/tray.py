"""System tray icon and menu."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class TrayIcon:
    """
    System tray icon for OpenSati.

    Shows current state and provides quick access to settings.
    """

    # Callbacks
    on_settings_click: Callable[[], None] | None = None
    on_quit_click: Callable[[], None] | None = None
    on_pause_click: Callable[[], None] | None = None
    on_intent_click: Callable[[], None] | None = None

    # Internal state
    _icon = None
    _running: bool = False
    _paused: bool = False

    def start(self) -> bool:
        """
        Start system tray icon.

        Returns True if successful.
        """
        try:
            import pystray
            from PIL import Image, ImageDraw

            # Create icon image
            icon_size = 64
            image = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)

            # Draw a circle (Sati symbol)
            margin = 8
            draw.ellipse(
                [margin, margin, icon_size - margin, icon_size - margin],
                outline="#4ADE80",
                width=4,
            )

            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("OpenSati", None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    "Set Intent...",
                    lambda: self._safe_callback(self.on_intent_click),
                ),
                pystray.MenuItem(
                    "Pause" if not self._paused else "Resume",
                    self._toggle_pause,
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    "Settings",
                    lambda: self._safe_callback(self.on_settings_click),
                ),
                pystray.MenuItem(
                    "Quit",
                    lambda: self._safe_callback(self.on_quit_click),
                ),
            )

            self._icon = pystray.Icon("opensati", image, "OpenSati", menu)
            self._running = True

            # Run in separate thread
            threading.Thread(target=self._icon.run, daemon=True).start()

            print("🔳 System tray started")
            return True

        except ImportError:
            print("⚠️ pystray not installed. Tray icon disabled.")
            return False
        except Exception as e:
            print(f"⚠️ Could not start tray: {e}")
            return False

    def _safe_callback(self, callback: Callable | None) -> None:
        """Safely call a callback."""
        if callback:
            callback()

    def _toggle_pause(self) -> None:
        """Toggle pause state."""
        self._paused = not self._paused

        if self.on_pause_click:
            self.on_pause_click()

        # Update tray icon would require recreation
        if self._paused:
            self.set_state("paused")
        else:
            self.set_state("active")

    def set_state(self, state: str) -> None:
        """
        Update tray icon to reflect state.

        States: active, paused, stress, flow
        """
        if not self._icon:
            return

        try:
            from PIL import Image, ImageDraw

            icon_size = 64
            image = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            margin = 8

            # Color based on state
            colors = {
                "active": "#4ADE80",   # Green
                "paused": "#6E6E73",   # Gray
                "stress": "#F97316",   # Orange
                "flow": "#818CF8",     # Purple
            }
            color = colors.get(state, "#4ADE80")

            # Draw circle (filled for stress/flow, outline for others)
            if state in ("stress", "flow"):
                draw.ellipse(
                    [margin, margin, icon_size - margin, icon_size - margin],
                    fill=color,
                )
            else:
                draw.ellipse(
                    [margin, margin, icon_size - margin, icon_size - margin],
                    outline=color,
                    width=4,
                )

            self._icon.icon = image

        except Exception as e:
            print(f"⚠️ Could not update tray icon: {e}")

    def stop(self) -> None:
        """Stop tray icon."""
        self._running = False
        if self._icon:
            self._icon.stop()
            self._icon = None
        print("🔳 System tray stopped")

    @property
    def is_paused(self) -> bool:
        """Check if monitoring is paused."""
        return self._paused
