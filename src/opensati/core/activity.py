"""
Activity monitoring for tracking active application and window title.

Tracks:
- Currently focused application name
- Active window title
- Time spent per application

Privacy: Titles logged locally only, never sent anywhere.
"""

from __future__ import annotations

import platform
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class ActivityState:
    """Current activity state."""
    
    app_name: str = ""
    window_title: str = ""
    bundle_id: str = ""
    
    # Usage stats
    usage_by_app: dict[str, float] = field(default_factory=dict)
    current_app_duration: float = 0.0


@dataclass
class ActivityMonitor:
    """
    Monitors active application and window title.
    
    Privacy: All data stays local. Only app names and durations logged.
    """
    
    # Callbacks
    on_app_switch: Callable[[str, str], None] | None = None  # (app_name, title)
    on_log: Callable[[str], None] | None = None
    
    # Configuration
    distracting_apps: list[str] = field(default_factory=lambda: [
        "Twitter", "Facebook", "Instagram", "TikTok", "Reddit",
        "YouTube", "Netflix", "Twitch", "Discord"
    ])
    distraction_threshold_minutes: int = 5
    
    # Internal state
    _current_app: str = ""
    _current_title: str = ""
    _current_bundle: str = ""
    _app_start_time: float = 0.0
    _usage_by_app: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    _running: bool = False
    
    def __post_init__(self):
        self._usage_by_app = defaultdict(float)
    
    def start(self) -> bool:
        """Start activity monitoring."""
        if platform.system() != "Darwin":
            if self.on_log:
                self.on_log("⚠️ Activity monitor only supports macOS currently")
            return False
        
        self._running = True
        self._app_start_time = time.time()
        
        # Get initial state
        self._update_state()
        
        if self.on_log:
            self.on_log(f"📊 Activity monitor started")
        
        return True
    
    def stop(self):
        """Stop monitoring."""
        self._running = False
        # Save final duration for current app
        if self._current_app and self._app_start_time:
            duration = time.time() - self._app_start_time
            self._usage_by_app[self._current_app] += duration
    
    def _get_active_app_mac(self) -> tuple[str, str, str]:
        """
        Get active application info on macOS.
        
        Returns (app_name, window_title, bundle_id).
        """
        try:
            from AppKit import NSWorkspace
            
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.frontmostApplication()
            
            app_name = active_app.localizedName() or ""
            bundle_id = active_app.bundleIdentifier() or ""
            
            # Try to get window title via Accessibility API
            window_title = self._get_window_title_mac(active_app)
            
            return (app_name, window_title, bundle_id)
            
        except Exception as e:
            # Fallback if AppKit fails
            return ("", "", "")
    
    def _get_window_title_mac(self, app) -> str:
        """Get window title using Accessibility API."""
        try:
            from Quartz import (
                CGWindowListCopyWindowInfo,
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID,
                kCGWindowOwnerPID,
                kCGWindowName,
                kCGWindowLayer
            )
            
            pid = app.processIdentifier()
            
            # Get all windows
            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly,
                kCGNullWindowID
            )
            
            # Find windows belonging to this app
            for window in window_list:
                if window.get(kCGWindowOwnerPID) == pid:
                    # Skip menu bar and other system windows
                    if window.get(kCGWindowLayer, 0) == 0:
                        title = window.get(kCGWindowName, "")
                        if title:
                            return title
            
            return ""
            
        except Exception:
            return ""
    
    def _update_state(self) -> bool:
        """
        Update current activity state.
        
        Returns True if app changed.
        """
        if platform.system() == "Darwin":
            app_name, title, bundle = self._get_active_app_mac()
        else:
            return False
        
        # Check if app changed
        app_changed = app_name != self._current_app
        
        if app_changed and self._current_app:
            # Log duration for previous app
            duration = time.time() - self._app_start_time
            self._usage_by_app[self._current_app] += duration
            
            # Notify about switch
            if self.on_app_switch:
                self.on_app_switch(app_name, title)
            
            if self.on_log:
                self.on_log(f"🔄 Switched to {app_name}: {title[:40]}..." if title else f"🔄 Switched to {app_name}")
        
        self._current_app = app_name
        self._current_title = title
        self._current_bundle = bundle
        
        if app_changed:
            self._app_start_time = time.time()
        
        return app_changed
    
    def check(self) -> ActivityState:
        """
        Check current activity and update stats.
        
        Call this periodically from the main loop.
        """
        if not self._running:
            return ActivityState()
        
        self._update_state()
        
        # Calculate current app duration
        current_duration = time.time() - self._app_start_time if self._app_start_time else 0
        
        # Check for distraction
        self._check_distraction(current_duration)
        
        # Build usage dict (copy with current app's live duration)
        usage = dict(self._usage_by_app)
        if self._current_app:
            usage[self._current_app] = usage.get(self._current_app, 0) + current_duration
        
        return ActivityState(
            app_name=self._current_app,
            window_title=self._current_title,
            bundle_id=self._current_bundle,
            usage_by_app=usage,
            current_app_duration=current_duration
        )
    
    def _check_distraction(self, duration: float):
        """Check if user is distracted and log warning."""
        if not self.on_log:
            return
        
        # Check if current app is in distracting list
        for distractor in self.distracting_apps:
            if distractor.lower() in self._current_app.lower() or \
               distractor.lower() in self._current_title.lower():
                
                minutes = duration / 60
                if minutes >= self.distraction_threshold_minutes:
                    # Only log once per threshold crossing (every 5 min increment)
                    if int(minutes) % self.distraction_threshold_minutes == 0 and \
                       int(minutes * 60) % 300 < 2:  # Within 2 seconds of threshold
                        self.on_log(f"⚠️ {int(minutes)} min on {distractor}")
                break
    
    def get_usage_summary(self) -> str:
        """Get a formatted summary of app usage."""
        # Get current stats
        state = self.check()
        
        if not state.usage_by_app:
            return "No usage data yet"
        
        # Sort by duration
        sorted_usage = sorted(
            state.usage_by_app.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5
        
        lines = ["📊 App Usage:"]
        for app, seconds in sorted_usage:
            minutes = seconds / 60
            if minutes >= 1:
                lines.append(f"  • {app}: {int(minutes)} min")
        
        return "\n".join(lines)
