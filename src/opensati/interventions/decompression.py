"""Meeting decompression screen."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

import customtkinter as ctk
import psutil

from opensati.config.settings import get_settings


@dataclass
class DecompressionScreen:
    """
    Full-screen calm overlay after meetings end.

    Provides a 60-second "palate cleanser" before context switching.
    """

    # Configuration
    duration: int = 60  # Seconds
    meeting_apps: list[str] = field(default_factory=list)

    # Callbacks
    on_complete: Callable[[], None] | None = None
    on_skip: Callable[[], None] | None = None

    # Internal state
    _window: ctk.CTkToplevel | None = None
    _active: bool = False
    _remaining: int = 0
    _was_in_meeting: bool = False
    _monitor_thread: threading.Thread | None = None
    _running: bool = False

    def __post_init__(self) -> None:
        """Initialize with settings."""
        settings = get_settings()
        if not self.meeting_apps:
            self.meeting_apps = settings.meeting.apps
        self.duration = settings.meeting.decompression_duration

    def start_monitoring(self) -> None:
        """Start monitoring for meeting app closures."""
        self._running = True

        def monitor():
            while self._running:
                in_meeting = self._check_meeting_active()

                # Detect transition from meeting to no-meeting
                if self._was_in_meeting and not in_meeting:
                    self.show()

                self._was_in_meeting = in_meeting
                time.sleep(5)  # Check every 5 seconds

        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()
        print("🎥 Meeting monitor started")

    def stop_monitoring(self) -> None:
        """Stop monitoring for meetings."""
        self._running = False
        print("🎥 Meeting monitor stopped")

    def _check_meeting_active(self) -> bool:
        """Check if any meeting app is running."""
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"]
                if name and any(
                    app.lower() in name.lower() for app in self.meeting_apps
                ):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def show(self) -> None:
        """Show decompression screen."""
        if self._active:
            return

        self._active = True
        self._remaining = self.duration

        def create():
            self._window = ctk.CTkToplevel()
            self._window.title("")
            self._window.attributes("-topmost", True)
            self._window.overrideredirect(True)

            # Full screen
            screen_width = self._window.winfo_screenwidth()
            screen_height = self._window.winfo_screenheight()
            self._window.geometry(f"{screen_width}x{screen_height}+0+0")

            # Dark, calm background
            self._window.configure(fg_color="#0A0A0B")

            # Center container
            container = ctk.CTkFrame(
                self._window, fg_color="transparent", width=400, height=200
            )
            container.place(relx=0.5, rely=0.5, anchor="center")

            # Breathing animation circle
            self._circle = ctk.CTkLabel(
                container,
                text="○",
                font=("Helvetica", 72),
                text_color="#4ADE80",
            )
            self._circle.pack(pady=20)

            # Message
            msg = ctk.CTkLabel(
                container,
                text="Meeting ended. Take a moment.",
                font=("Inter", 18),
                text_color="#A1A1A6",
            )
            msg.pack(pady=10)

            # Timer
            self._timer_label = ctk.CTkLabel(
                container,
                text=f"{self._remaining}s",
                font=("Inter", 24, "bold"),
                text_color="#F5F5F7",
            )
            self._timer_label.pack(pady=20)

            # Skip button (subtle)
            skip_btn = ctk.CTkButton(
                container,
                text="Skip",
                width=60,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#2C2C2E",
                text_color="#6E6E73",
                command=self._skip,
            )
            skip_btn.pack(pady=10)

            # Start countdown
            self._countdown()

        if threading.current_thread() is threading.main_thread():
            create()

        print("🧘 Decompression started - breathe...")

    def _countdown(self) -> None:
        """Run countdown timer."""
        if not self._active or not self._window:
            return

        if self._remaining <= 0:
            self.hide()
            if self.on_complete:
                self.on_complete()
            return

        # Update timer display
        if hasattr(self, "_timer_label") and self._timer_label:
            self._timer_label.configure(text=f"{self._remaining}s")

        # Pulse the circle
        if hasattr(self, "_circle"):
            scale = 1.0 + 0.1 * abs((self._remaining % 8) - 4) / 4
            size = int(72 * scale)
            self._circle.configure(font=("Helvetica", size))

        self._remaining -= 1

        # Schedule next tick
        if self._window:
            self._window.after(1000, self._countdown)

    def _skip(self) -> None:
        """Skip decompression."""
        self.hide()
        if self.on_skip:
            self.on_skip()
        print("⏭️ Decompression skipped")

    def hide(self) -> None:
        """Hide decompression screen."""
        self._active = False
        if self._window:
            self._window.destroy()
            self._window = None

    def is_active(self) -> bool:
        """Check if decompression is active."""
        return self._active
