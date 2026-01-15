"""Settings window UI."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import customtkinter as ctk

from opensati.config.settings import Settings, get_settings


@dataclass
class SettingsWindow:
    """
    Settings window for OpenSati configuration.

    Design based on OpenSati Design System.
    """

    # Callbacks
    on_save: Callable[[Settings], None] | None = None
    on_close: Callable[[], None] | None = None

    # Internal state
    _window: ctk.CTkToplevel | None = None
    _settings: Settings | None = None

    def show(self) -> None:
        """Show settings window."""
        if self._window is not None:
            self._window.focus()
            return

        self._settings = get_settings()

        # Create window
        self._window = ctk.CTkToplevel()
        self._window.title("OpenSati Settings")
        self._window.geometry("500x600")
        self._window.resizable(False, False)

        # Configure appearance
        ctk.set_appearance_mode("dark")

        # Main container with padding
        container = ctk.CTkFrame(self._window, fg_color="#0A0A0B")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            container,
            text="⚙️ Settings",
            font=("Inter", 24, "bold"),
            text_color="#F5F5F7",
        )
        title.pack(anchor="w", pady=(0, 20))

        # Scrollable frame for settings
        scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            height=450,
        )
        scroll.pack(fill="both", expand=True)

        # === Sensors Section ===
        self._create_section(scroll, "🔒 Privacy & Sensors")

        self._keyboard_var = ctk.BooleanVar(value=self._settings.sensors.keyboard)
        self._create_toggle(
            scroll, "Keyboard monitoring", self._keyboard_var, "Low risk - velocity only"
        )

        self._mouse_var = ctk.BooleanVar(value=self._settings.sensors.mouse)
        self._create_toggle(
            scroll, "Mouse monitoring", self._mouse_var, "Low risk - patterns only"
        )

        self._screen_var = ctk.BooleanVar(value=self._settings.sensors.screen)
        self._create_toggle(
            scroll, "Screen analysis", self._screen_var, "For intent checking (RAM only)"
        )

        self._webcam_var = ctk.BooleanVar(value=self._settings.sensors.webcam)
        self._create_toggle(
            scroll, "Webcam posture", self._webcam_var, "For posture detection (not stored)"
        )

        self._mic_var = ctk.BooleanVar(value=self._settings.sensors.microphone)
        self._create_toggle(
            scroll, "Microphone", self._mic_var, "For breathing analysis (not stored)"
        )

        # === Detection Section ===
        self._create_section(scroll, "🎯 Detection")

        self._threshold_var = ctk.IntVar(value=self._settings.detection.stress_threshold)
        self._create_slider(
            scroll, "Stress threshold", self._threshold_var, 20, 100, "Keystrokes/10s"
        )

        # === Intervention Section ===
        self._create_section(scroll, "🌑 Intervention")

        self._style_var = ctk.StringVar(value=self._settings.intervention.style)
        self._create_dropdown(
            scroll,
            "Intervention style",
            self._style_var,
            ["grayscale", "blur", "notification"],
        )

        self._cooldown_var = ctk.IntVar(value=self._settings.intervention.cooldown)
        self._create_slider(
            scroll, "Cooldown", self._cooldown_var, 30, 300, "seconds between"
        )

        # === Privacy Status ===
        self._create_section(scroll, "🔐 Privacy Status")

        status_frame = ctk.CTkFrame(scroll, fg_color="#141415", corner_radius=8)
        status_frame.pack(fill="x", pady=5)

        status_text = """🔒 All data stays local
├─ Screenshots: RAM only, deleted
├─ Audio: Analyzed live, not stored
├─ Network: 0 bytes sent
└─ AI: 100% Local (Ollama)"""

        status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=("JetBrains Mono", 11),
            text_color="#4ADE80",
            justify="left",
        )
        status_label.pack(padx=15, pady=15, anchor="w")

        # Save button
        save_btn = ctk.CTkButton(
            container,
            text="Save Settings",
            height=40,
            corner_radius=8,
            fg_color="#4ADE80",
            hover_color="#22C55E",
            text_color="#000000",
            font=("Inter", 14, "bold"),
            command=self._save,
        )
        save_btn.pack(fill="x", pady=(20, 0))

        # Handle close
        self._window.protocol("WM_DELETE_WINDOW", self._close)

    def _create_section(self, parent: ctk.CTkFrame, title: str) -> None:
        """Create a section header."""
        label = ctk.CTkLabel(
            parent,
            text=title,
            font=("Inter", 14, "bold"),
            text_color="#F5F5F7",
        )
        label.pack(anchor="w", pady=(20, 10))

    def _create_toggle(
        self,
        parent: ctk.CTkFrame,
        label: str,
        variable: ctk.BooleanVar,
        description: str,
    ) -> None:
        """Create a toggle with description."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        text_frame = ctk.CTkFrame(frame, fg_color="transparent")
        text_frame.pack(side="left", fill="x", expand=True)

        lbl = ctk.CTkLabel(
            text_frame,
            text=label,
            font=("Inter", 13),
            text_color="#F5F5F7",
        )
        lbl.pack(anchor="w")

        desc = ctk.CTkLabel(
            text_frame,
            text=description,
            font=("Inter", 11),
            text_color="#6E6E73",
        )
        desc.pack(anchor="w")

        switch = ctk.CTkSwitch(
            frame,
            text="",
            variable=variable,
            onvalue=True,
            offvalue=False,
            progress_color="#4ADE80",
        )
        switch.pack(side="right")

    def _create_slider(
        self,
        parent: ctk.CTkFrame,
        label: str,
        variable: ctk.IntVar,
        min_val: int,
        max_val: int,
        unit: str,
    ) -> None:
        """Create a slider with value display."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        lbl = ctk.CTkLabel(
            frame,
            text=label,
            font=("Inter", 13),
            text_color="#F5F5F7",
        )
        lbl.pack(anchor="w")

        slider_frame = ctk.CTkFrame(frame, fg_color="transparent")
        slider_frame.pack(fill="x", pady=5)

        value_label = ctk.CTkLabel(
            slider_frame,
            text=f"{variable.get()} {unit}",
            font=("Inter", 12),
            text_color="#A1A1A6",
            width=100,
        )
        value_label.pack(side="right")

        def on_change(val):
            variable.set(int(val))
            value_label.configure(text=f"{int(val)} {unit}")

        slider = ctk.CTkSlider(
            slider_frame,
            from_=min_val,
            to=max_val,
            variable=variable,
            command=on_change,
            progress_color="#4ADE80",
        )
        slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def _create_dropdown(
        self,
        parent: ctk.CTkFrame,
        label: str,
        variable: ctk.StringVar,
        options: list[str],
    ) -> None:
        """Create a dropdown menu."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)

        lbl = ctk.CTkLabel(
            frame,
            text=label,
            font=("Inter", 13),
            text_color="#F5F5F7",
        )
        lbl.pack(side="left")

        dropdown = ctk.CTkOptionMenu(
            frame,
            variable=variable,
            values=options,
            fg_color="#1C1C1E",
            button_color="#2C2C2E",
            button_hover_color="#3A3A3C",
            dropdown_fg_color="#1C1C1E",
            dropdown_hover_color="#2C2C2E",
        )
        dropdown.pack(side="right")

    def _save(self) -> None:
        """Save settings."""
        if self._settings:
            # Update settings from UI
            self._settings.sensors.keyboard = self._keyboard_var.get()
            self._settings.sensors.mouse = self._mouse_var.get()
            self._settings.sensors.screen = self._screen_var.get()
            self._settings.sensors.webcam = self._webcam_var.get()
            self._settings.sensors.microphone = self._mic_var.get()
            self._settings.detection.stress_threshold = self._threshold_var.get()
            self._settings.intervention.style = self._style_var.get()
            self._settings.intervention.cooldown = self._cooldown_var.get()

            # Save to disk
            self._settings.save()

            if self.on_save:
                self.on_save(self._settings)

        self._close()

    def _close(self) -> None:
        """Close window."""
        if self._window:
            self._window.destroy()
            self._window = None

        if self.on_close:
            self.on_close()

    def is_open(self) -> bool:
        """Check if window is open."""
        return self._window is not None
