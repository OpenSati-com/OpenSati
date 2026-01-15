"""
macOS-specific input monitoring using Quartz CGEventTap.

Bypasses pynput to avoid pyobjc compatibility issues.
Only captures event timing/count, never key content.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class MacInputMonitor:
    """Monitor keyboard/mouse activity using Quartz (macOS only)."""
    
    window_size: float = 10.0
    
    # Internal state
    _event_times: deque = field(default_factory=lambda: deque(maxlen=500))
    _running: bool = False
    _thread: threading.Thread | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def __post_init__(self):
        self._event_times = deque(maxlen=500)
        self._lock = threading.Lock()
    
    def start(self) -> bool:
        """Start monitoring. Returns True if successful."""
        if self._running:
            return True
            
        try:
            from Quartz import (
                CGEventTapCreate, kCGSessionEventTap, kCGHeadInsertEventTap,
                kCGEventTapOptionListenOnly, CGEventMaskBit, 
                kCGEventKeyDown, kCGEventMouseMoved, kCGEventLeftMouseDown,
                CFMachPortCreateRunLoopSource, CFRunLoopGetCurrent,
                CFRunLoopAddSource, kCFRunLoopCommonModes, CFRunLoopRun,
                CGEventTapEnable
            )
        except ImportError:
            print("⚠️ Quartz not available")
            return False
        
        def callback(proxy, event_type, event, refcon):
            """Record event timestamp (not content)."""
            with self._lock:
                self._event_times.append(time.time())
            return event
        
        # Create event tap for keyboard and mouse
        mask = (CGEventMaskBit(kCGEventKeyDown) | 
                CGEventMaskBit(kCGEventMouseMoved) |
                CGEventMaskBit(kCGEventLeftMouseDown))
        
        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            kCGEventTapOptionListenOnly,
            mask,
            callback,
            None
        )
        
        if tap is None:
            print("⚠️ Could not create event tap - grant Accessibility permission to Terminal")
            print("   Go to: System Settings → Privacy & Security → Accessibility → add Terminal")
            return False
        
        def run_loop():
            from Quartz import (
                CFMachPortCreateRunLoopSource, CFRunLoopGetCurrent,
                CFRunLoopAddSource, kCFRunLoopCommonModes, CFRunLoopRun,
                CGEventTapEnable
            )
            source = CFMachPortCreateRunLoopSource(None, tap, 0)
            CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes)
            CGEventTapEnable(tap, True)
            CFRunLoopRun()
        
        self._running = True
        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        
        print("🎹 Input monitoring started (Quartz)")
        return True
    
    def stop(self):
        """Stop monitoring."""
        self._running = False
        # Note: CFRunLoop needs proper cleanup in production
        
    def get_events_per_second(self) -> float:
        """Get input events per second in the window."""
        now = time.time()
        window_start = now - self.window_size
        
        with self._lock:
            recent = sum(1 for t in self._event_times if t > window_start)
        
        return recent / self.window_size
    
    def get_intensity(self) -> float:
        """Get input intensity as 0-100 score."""
        eps = self.get_events_per_second()
        # Normalize: 0-5 events/sec = 0-100%
        return min(100, eps * 20)
