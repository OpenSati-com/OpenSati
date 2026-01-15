"""
Floating status widget for OpenSati.

Draggable widget with expandable log panel.
Click the arrow button to toggle log view.
"""

from __future__ import annotations

import customtkinter as ctk
from collections import deque
from datetime import datetime


class FloatingWidget:
    """Draggable floating widget with expandable log panel."""

    def __init__(
        self,
        root: ctk.CTk,
        on_click: callable | None = None,
        on_right_click: callable | None = None,
    ):
        self.root = root
        self.on_click = on_click
        self.on_right_click = on_right_click
        self._dragged = False
        self._expanded = False
        self._logs = deque(maxlen=50)

        # Configure root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.geometry("80x80+50+50")
        self.root.configure(fg_color="#1C1C1E")

        # Main container
        self.container = ctk.CTkFrame(self.root, fg_color="#1C1C1E", corner_radius=20)
        self.container.pack(fill="both", expand=True)

        # Status button (the main circle)
        self.button = ctk.CTkButton(
            self.container,
            text="👁️",
            font=("", 28),
            width=60,
            height=60,
            corner_radius=30,
            fg_color="#4ADE80",
            hover_color="#22C55E",
            command=self._on_button_click
        )
        self.button.pack(pady=(8, 2))

        # Expand toggle (small arrow button)
        self.toggle_btn = ctk.CTkButton(
            self.container,
            text="▼",
            font=("", 10),
            width=30,
            height=14,
            corner_radius=7,
            fg_color="#3A3A3C",
            hover_color="#48484A",
            command=self.toggle_expand
        )
        self.toggle_btn.pack(pady=(0, 4))

        # Log panel frame (hidden initially)
        self.log_frame = ctk.CTkFrame(self.container, fg_color="#2C2C2E", corner_radius=10)
        
        # Log textbox
        self.log_text = ctk.CTkTextbox(
            self.log_frame,
            width=280,
            height=200,
            font=("Menlo", 11),
            fg_color="#1C1C1E",
            text_color="#A0A0A0",
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_text.configure(state="disabled")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(self.log_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        ctk.CTkButton(
            btn_frame, text="⚙️ Settings", width=90, height=28,
            command=lambda: self.on_click() if self.on_click else None
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame, text="⏸️ Pause", width=70, height=28,
            command=lambda: self.on_right_click(None) if self.on_right_click else None
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            btn_frame, text="🗑️ Clear", width=60, height=28,
            command=self._clear_log
        ).pack(side="right", padx=2)

        # Drag state
        self._drag_data = {"x": 0, "y": 0}

        # Bind drag to container (not button, so button clicks work)
        self.container.bind("<Button-1>", self._on_press)
        self.container.bind("<B1-Motion>", self._on_drag)
        
        # Initial log
        self.log("🧘 OpenSati started")

    def _on_button_click(self):
        """Main button clicked - show settings."""
        if self.on_click:
            self.on_click()

    def _on_press(self, event):
        """Start drag."""
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root

    def _on_drag(self, event):
        """Drag the widget."""
        x = self.root.winfo_x() + (event.x_root - self._drag_data["x"])
        y = self.root.winfo_y() + (event.y_root - self._drag_data["y"])
        self.root.geometry(f"+{x}+{y}")
        self._drag_data["x"] = event.x_root
        self._drag_data["y"] = event.y_root

    def toggle_expand(self):
        """Toggle log panel."""
        self._expanded = not self._expanded
        x, y = self.root.winfo_x(), self.root.winfo_y()
        
        if self._expanded:
            self.log_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
            self.root.geometry(f"300x350+{x}+{y}")
            self.toggle_btn.configure(text="▲")
            self.log("📋 Log panel opened")
        else:
            self.log_frame.pack_forget()
            self.root.geometry(f"80x80+{x}+{y}")
            self.toggle_btn.configure(text="▼")

    def _clear_log(self):
        """Clear log entries."""
        self._logs.clear()
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.log("🗑️ Log cleared")

    def log(self, message: str):
        """Add timestamped log entry."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self._logs.append(entry)
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", entry + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def set_color(self, color: str):
        """Update button color."""
        self.button.configure(fg_color=color)

    def set_status(self, status: str):
        """Update status and log it."""
        config = {
            "stress": ("#F97316", "⚡", "Stress detected"),
            "flow": ("#818CF8", "🌊", "Flow state"),
            "paused": ("#6E6E73", "⏸️", "Paused"),
            "active": ("#4ADE80", "👁️", "Monitoring"),
        }
        color, icon, msg = config.get(status, ("#4ADE80", "👁️", "Active"))
        self.set_color(color)
        self.button.configure(text=icon)
        self.log(f"Status: {msg}")
