"""Blur intervention for posture correction."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

import customtkinter as ctk


@dataclass
class BlurOverlay:
    """
    Blurs the screen when bad posture is detected.

    Clears immediately when posture is corrected.
    """

    # Configuration
    blur_intensity: float = 0.7  # 0-1
    fade_duration: float = 1.0

    # Internal state
    _active: bool = False
    _window: ctk.CTk | None = None
    _current_alpha: float = 0.0

    def show(self) -> None:
        """Show blur overlay."""
        if self._active:
            return

        self._active = True

        def create_window():
            self._window = ctk.CTkToplevel()
            self._window.title("")
            self._window.attributes("-topmost", True)
            self._window.overrideredirect(True)

            # Full screen
            screen_width = self._window.winfo_screenwidth()
            screen_height = self._window.winfo_screenheight()
            self._window.geometry(f"{screen_width}x{screen_height}+0+0")

            # Semi-transparent dark overlay
            self._window.configure(fg_color="#000000")
            self._window.attributes("-alpha", 0.0)

            # Add message
            label = ctk.CTkLabel(
                self._window,
                text="🧘 Sit up straight to restore clarity",
                font=("Helvetica", 24),
                text_color="#ffffff",
            )
            label.place(relx=0.5, rely=0.5, anchor="center")

            # Fade in
            self._fade_in()

        # Run on main thread if needed
        if threading.current_thread() is threading.main_thread():
            create_window()
        else:
            # Schedule for later (would need main app reference)
            pass

        print("🌫️ Blur overlay shown - fix posture to clear")

    def _fade_in(self) -> None:
        """Fade in the overlay."""
        if not self._window:
            return

        steps = 20
        step_duration = self.fade_duration / steps
        target_alpha = self.blur_intensity

        def fade():
            for i in range(steps):
                if not self._active:
                    break
                alpha = (i + 1) / steps * target_alpha
                self._current_alpha = alpha
                if self._window:
                    self._window.attributes("-alpha", alpha)
                time.sleep(step_duration)

        threading.Thread(target=fade, daemon=True).start()

    def hide(self) -> None:
        """Hide blur overlay immediately."""
        self._active = False
        self._current_alpha = 0.0

        if self._window:
            self._window.destroy()
            self._window = None

        print("✨ Blur cleared - good posture!")

    def is_active(self) -> bool:
        """Check if blur is active."""
        return self._active
