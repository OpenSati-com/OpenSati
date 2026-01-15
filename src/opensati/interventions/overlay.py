"""Notification overlay for interventions."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass

import customtkinter as ctk


@dataclass
class NotificationOverlay:
    """
    Floating notification pill for interventions.

    Design based on OpenSati Design System.
    """

    # Callbacks
    on_accept: Callable[[], None] | None = None
    on_dismiss: Callable[[], None] | None = None

    # Internal state
    _window: ctk.CTkToplevel | None = None
    _visible: bool = False

    def show(
        self,
        message: str,
        title: str = "OpenSati",
        accept_text: str = "Yes",
        dismiss_text: str = "Not now",
    ) -> None:
        """Show notification pill."""
        if self._visible:
            return

        self._visible = True

        def create():
            # Create toplevel window
            self._window = ctk.CTkToplevel()
            self._window.title("")
            self._window.attributes("-topmost", True)
            self._window.overrideredirect(True)

            # Size and position (bottom center)
            width = 420
            height = 100
            screen_width = self._window.winfo_screenwidth()
            screen_height = self._window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = screen_height - height - 50

            self._window.geometry(f"{width}x{height}+{x}+{y}")

            # Styling (based on design system)
            self._window.configure(fg_color="#1C1C1E")  # --bg-elevated

            # Main frame with border
            frame = ctk.CTkFrame(
                self._window,
                corner_radius=12,
                fg_color="#1C1C1E",
                border_color="#3A3A3C",  # --border-default
                border_width=1,
            )
            frame.pack(fill="both", expand=True, padx=2, pady=2)

            # Status indicator
            indicator = ctk.CTkLabel(
                frame,
                text="○",
                font=("Helvetica", 16),
                text_color="#F97316",  # --accent-alert
            )
            indicator.pack(side="left", padx=(16, 8))

            # Text container
            text_frame = ctk.CTkFrame(frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, pady=12)

            # Message
            msg_label = ctk.CTkLabel(
                text_frame,
                text=message,
                font=("Inter", 14),
                text_color="#F5F5F7",  # --text-primary
                anchor="w",
            )
            msg_label.pack(anchor="w")

            # Buttons
            btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
            btn_frame.pack(side="right", padx=16)

            accept_btn = ctk.CTkButton(
                btn_frame,
                text=accept_text,
                width=70,
                height=32,
                corner_radius=8,
                fg_color="#4ADE80",  # --accent-calm
                hover_color="#22C55E",
                text_color="#000000",
                command=self._on_accept_click,
            )
            accept_btn.pack(side="left", padx=4)

            dismiss_btn = ctk.CTkButton(
                btn_frame,
                text=dismiss_text,
                width=80,
                height=32,
                corner_radius=8,
                fg_color="transparent",
                hover_color="#2C2C2E",
                border_width=1,
                border_color="#3A3A3C",
                text_color="#A1A1A6",  # --text-secondary
                command=self._on_dismiss_click,
            )
            dismiss_btn.pack(side="left", padx=4)

            # Start invisible, then fade in
            self._window.attributes("-alpha", 0.0)
            self._fade_in()

        # Must run on main thread
        if threading.current_thread() is threading.main_thread():
            create()
        else:
            # Would need reference to main app to schedule
            pass

    def _fade_in(self) -> None:
        """Fade in animation."""
        if not self._window:
            return

        def fade():
            for i in range(10):
                if not self._visible or not self._window:
                    break
                alpha = (i + 1) / 10 * 0.95
                self._window.attributes("-alpha", alpha)
                time.sleep(0.02)

        threading.Thread(target=fade, daemon=True).start()

    def _on_accept_click(self) -> None:
        """Handle accept button click."""
        self.hide()
        if self.on_accept:
            self.on_accept()

    def _on_dismiss_click(self) -> None:
        """Handle dismiss button click."""
        self.hide()
        if self.on_dismiss:
            self.on_dismiss()

    def hide(self) -> None:
        """Hide notification."""
        self._visible = False
        if self._window:
            self._window.destroy()
            self._window = None

    def is_visible(self) -> bool:
        """Check if notification is visible."""
        return self._visible
