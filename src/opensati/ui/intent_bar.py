"""Intent input bar widget."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import customtkinter as ctk


@dataclass
class IntentBar:
    """
    Floating intent input bar.

    Allows user to declare their work focus.
    """

    # Callbacks
    on_submit: Callable[[str], None] | None = None
    on_clear: Callable[[], None] | None = None

    # Internal state
    _window: ctk.CTkToplevel | None = None
    _entry: ctk.CTkEntry | None = None
    _current_intent: str = ""

    def show(self, current_intent: str = "") -> None:
        """Show intent input bar."""
        if self._window is not None:
            self._window.focus()
            return

        self._current_intent = current_intent

        # Create window
        self._window = ctk.CTkToplevel()
        self._window.title("")
        self._window.attributes("-topmost", True)
        self._window.overrideredirect(True)

        # Size and position (top center)
        width = 500
        height = 60
        screen_width = self._window.winfo_screenwidth()
        x = (screen_width - width) // 2
        y = 50

        self._window.geometry(f"{width}x{height}+{x}+{y}")
        self._window.configure(fg_color="#1C1C1E")

        # Main frame with border
        frame = ctk.CTkFrame(
            self._window,
            corner_radius=12,
            fg_color="#1C1C1E",
            border_color="#3A3A3C",
            border_width=1,
        )
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        # Icon
        icon = ctk.CTkLabel(
            frame,
            text="🎯",
            font=("Helvetica", 20),
        )
        icon.pack(side="left", padx=(16, 8))

        # Entry
        self._entry = ctk.CTkEntry(
            frame,
            placeholder_text="What are you working on?",
            font=("Inter", 14),
            fg_color="transparent",
            border_width=0,
            text_color="#F5F5F7",
            placeholder_text_color="#6E6E73",
        )
        self._entry.pack(side="left", fill="both", expand=True, padx=8)

        if current_intent:
            self._entry.insert(0, current_intent)

        self._entry.bind("<Return>", self._on_enter)
        self._entry.bind("<Escape>", self._on_escape)

        # Clear button (if intent exists)
        if current_intent:
            clear_btn = ctk.CTkButton(
                frame,
                text="Clear",
                width=60,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#2C2C2E",
                text_color="#6E6E73",
                command=self._clear_intent,
            )
            clear_btn.pack(side="right", padx=8)

        # Submit button
        submit_btn = ctk.CTkButton(
            frame,
            text="Set",
            width=50,
            height=28,
            corner_radius=6,
            fg_color="#4ADE80",
            hover_color="#22C55E",
            text_color="#000000",
            command=self._submit,
        )
        submit_btn.pack(side="right", padx=(0, 8))

        # Focus entry
        self._entry.focus()

        # Fade in
        self._window.attributes("-alpha", 0.0)
        self._fade_in()

    def _fade_in(self) -> None:
        """Fade in animation."""
        if not self._window:
            return

        import threading
        import time

        def fade():
            for i in range(10):
                if not self._window:
                    break
                alpha = (i + 1) / 10 * 0.95
                self._window.attributes("-alpha", alpha)
                time.sleep(0.02)

        threading.Thread(target=fade, daemon=True).start()

    def _on_enter(self, event) -> None:
        """Handle enter key."""
        self._submit()

    def _on_escape(self, event) -> None:
        """Handle escape key."""
        self.hide()

    def _submit(self) -> None:
        """Submit intent."""
        if self._entry:
            intent = self._entry.get().strip()
            if intent and self.on_submit:
                self.on_submit(intent)
        self.hide()

    def _clear_intent(self) -> None:
        """Clear intent."""
        if self.on_clear:
            self.on_clear()
        self.hide()

    def hide(self) -> None:
        """Hide intent bar."""
        if self._window:
            self._window.destroy()
            self._window = None
            self._entry = None

    def is_visible(self) -> bool:
        """Check if intent bar is visible."""
        return self._window is not None
