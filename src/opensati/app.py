"""Main OpenSati application."""

from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass, field

import customtkinter as ctk

from opensati.config.settings import Settings, get_settings
from opensati.core.detector import StressDetector, StressLevel
from opensati.core.vision import ScreenCapture
from opensati.interventions.decompression import DecompressionScreen
from opensati.interventions.grayscale import GrayscaleEffect
from opensati.interventions.overlay import NotificationOverlay
from opensati.ui.intent_bar import IntentBar
from opensati.ui.settings import SettingsWindow
from opensati.ui.tray import TrayIcon


@dataclass
class OpenSatiApp:
    """
    Main OpenSati application.

    Orchestrates all components for the intelligent mirror.
    """

    # Configuration
    settings: Settings = field(default_factory=get_settings)

    # Core components
    _detector: StressDetector | None = None
    _grayscale: GrayscaleEffect | None = None
    _notification: NotificationOverlay | None = None
    _decompression: DecompressionScreen | None = None
    _tray: TrayIcon | None = None
    _settings_window: SettingsWindow | None = None
    _intent_bar: IntentBar | None = None

    # AI components (optional)
    _intent_checker = None
    _screen_capture: ScreenCapture | None = None

    # State
    _running: bool = False
    _monitor_thread: threading.Thread | None = None
    _root: ctk.CTk | None = None

    def __post_init__(self) -> None:
        """Initialize components."""
        self._setup_components()

    def _setup_components(self) -> None:
        """Set up all application components."""
        # Core detector
        self._detector = StressDetector(
            settings=self.settings,
            on_stress_detected=self._on_stress_detected,
            on_calm_restored=self._on_calm_restored,
        )

        # Interventions
        self._grayscale = GrayscaleEffect(
            fade_duration=self.settings.intervention.fade_duration,
        )

        self._notification = NotificationOverlay(
            on_accept=self._on_intervention_accept,
            on_dismiss=self._on_intervention_dismiss,
        )

        self._decompression = DecompressionScreen()

        # UI
        self._tray = TrayIcon(
            on_settings_click=self._show_settings,
            on_quit_click=self._quit,
            on_pause_click=self._toggle_pause,
            on_intent_click=self._show_intent_bar,
        )

        self._settings_window = SettingsWindow(
            on_save=self._on_settings_save,
        )

        self._intent_bar = IntentBar(
            on_submit=self._on_intent_set,
            on_clear=self._on_intent_clear,
        )

        # Set up intent checker if screen analysis enabled
        if self.settings.sensors.screen:
            self._setup_intent_checker()
            # Initialize screen capture
            self._screen_capture = ScreenCapture(capture_interval=15.0)
            print("🖥️ Screen analysis enabled")

    def _setup_intent_checker(self) -> None:
        """Set up optional intent checking."""
        try:
            from opensati.ai.intent import IntentChecker

            self._intent_checker = IntentChecker(
                on_mismatch_detected=self._on_intent_mismatch,
                on_log=self._log,
            )
        except ImportError:
            print("⚠️ Intent checker not available")

    def run(self) -> None:
        """Run the application."""
        print("\n" + "=" * 50)
        print("🧘 OpenSati - The Intelligent Mirror for Deep Work")
        print("=" * 50)
        print("\n🔒 Privacy Mode: All data stays local\n")

        # Initialize customtkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Create hidden root window
        self._root = ctk.CTk()
        self._root.withdraw()  # Hide main window

        # Start components
        self._start()

        # Fallback: If tray failed to start (e.g. macOS), use Floating Widget
        if self._tray and not self._tray._running:
            print("ℹ️ Tray disabled - switching to Floating Widget mode")
            
            from opensati.ui.widget import FloatingWidget
            
            # Use the root window as the floating widget
            self._root.deiconify()
            self._widget = FloatingWidget(
                self._root,
                on_click=self._show_settings,
                on_right_click=self._show_context_menu
            )
            
            # Ensure quitting works via right-click or other means
            # We don't have a taskbar icon, so user relies on the widget

        # Run main loop
        try:
            self._root.mainloop()
        except KeyboardInterrupt:
            self._quit()

    def _show_context_menu(self, event=None):
        """Handle right click on widget (Toggle Pause)."""
        # Reuse tray logic to toggle pause state
        if self._tray:
            # This toggles boolean, calls callback, and tries to update icon (fails safely)
            self._tray._toggle_pause()

    def _update_widget_state(self, state: str) -> None:
        """Update floating widget appearance."""
        if hasattr(self, "_widget"):
            self._widget.set_status(state)

    def _log(self, message: str) -> None:
        """Log message to widget if available."""
        if hasattr(self, "_widget"):
            self._widget.log(message)

    def _start(self) -> None:
        """Start monitoring and UI."""
        self._running = True

        # Start detector
        if self._detector:
            self._detector.start()

        # Start meeting decompression monitor
        if self._decompression:
            self._decompression.start_monitoring()

        # Start intent checker if enabled
        if self._intent_checker and self.settings.sensors.screen:
            self._intent_checker.start()
            # Set default intent to enable immediate analysis
            self._intent_checker.set_intent("General Productivity")
            self._log("🎯 Default goal set: General Productivity")

        # Start system tray
        if self._tray:
            self._tray.start()

        # Start monitoring loop
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True
        )
        self._monitor_thread.start()

        print("✅ OpenSati running. Access settings from the system tray.")

    def _monitor_loop(self) -> None:
        """Main monitoring loop with activity logging."""
        check_interval = 2.0  # Seconds
        log_interval = 5.0    # Log every 5 seconds
        last_log_time = 0

        while self._running:
            time.sleep(check_interval)

            # Skip if paused
            if self._tray and self._tray.is_paused:
                self._log("⏸️ Monitoring paused...")
                continue

            # Get detector state and log periodically
            if self._detector:
                state = self._detector.get_state()
                current_time = time.time()
                
                # Log sensor data every log_interval seconds
                if current_time - last_log_time >= log_interval:
                    last_log_time = current_time
                    
                    # Check and log sensor status
                    sensors_active = False
                    
                    # Log typing rate or show guidance
                    if state.input_score > 0:
                        self._log(f"⌨️ Typing: {state.input_score:.0f}% intensity")
                        sensors_active = True
                    elif self._detector._input_sensor and not self._detector._input_sensor._running:
                        # Sensor exists but not running - needs permissions
                        self._log("⚠️ Input sensors disabled - needs Accessibility permission")
                    
                    # Log breathing if available
                    if state.breathing_score > 0:
                        self._log(f"🫁 Breathing: {state.breathing_score:.0f}% stress")
                        sensors_active = True
                    
                    # Log posture if available  
                    if state.posture_score > 0:
                        self._log(f"🪑 Posture: {state.posture_score:.0f}% tension")
                        sensors_active = True
                    
                    # Log overall stress
                    self._log(f"📊 Stress level: {state.score:.0f}/100 ({state.level.value})")

                    # Screen analysis
                    if hasattr(self, "_screen_capture") and self._screen_capture:
                        # Periodically capture screen (every 3rd log cycle to save resources)
                        if int(current_time) % 15 < 2:
                            self._screen_capture.capture()
                        
                        screen_state = self._screen_capture.get_state()
                        if screen_state.has_screenshot:
                            self._log(f"🖥️ Screen: Active (Brightness: {screen_state.brightness:.1f})")
                            sensors_active = True
                    
                    # Show guidance if no sensors active
                    if not sensors_active and state.score == 0:
                        self._log("💡 Add Terminal to: System Settings → Privacy → Accessibility")
                
                # Check and intervene
                self._detector.check_and_intervene()

            # Check intent if enabled
            if self._intent_checker:
                self._intent_checker.check()

    def _on_stress_detected(self, level: StressLevel, score: float) -> None:
        """Handle stress detection."""
        print(f"⚡ Stress detected: {level.value} ({score:.0f})")

        # Update tray icon
        if self._tray:
            self._tray.set_state("stress")
            
        self._update_widget_state("stress")

        # Apply intervention based on style
        style = self.settings.intervention.style

        if style == "grayscale" and self._grayscale:
            self._grayscale.start_fade()
            # Also show notification
            if self._notification:
                self._show_notification("You're typing fast. Take a breath?")

        elif style == "blur":
            # Use blur overlay
            pass

        elif style == "notification" and self._notification:
            self._show_notification("Stress detected. Would you like to pause?")

    def _on_calm_restored(self) -> None:
        """Handle return to calm state."""
        print("🌿 Calm restored")

        # Update tray icon
        if self._tray:
            self._tray.set_state("active")
            
        self._update_widget_state("active")

    def _show_notification(self, message: str) -> None:
        """Show intervention notification (thread-safe)."""
        if self._root and self._notification:
            self._root.after(0, lambda: self._notification.show(message))

    def _on_intervention_accept(self) -> None:
        """Handle user accepting intervention."""
        print("🧘 User accepted intervention")

        # Restore color
        if self._grayscale and self._grayscale.is_active():
            self._grayscale.restore()

        # Update tray
        if self._tray:
            self._tray.set_state("flow")
            
        self._update_widget_state("flow")

    def _on_intervention_dismiss(self) -> None:
        """Handle user dismissing intervention."""
        print("⏭️ User dismissed intervention")
        # Grayscale will auto-restore after hold duration

    def _on_intent_mismatch(self, intent: str, explanation: str) -> None:
        """Handle intent-reality mismatch."""
        print(f"❓ Intent mismatch: {explanation}")

        message = f'Is this part of "{intent}"?'
        if self._notification:
            self._show_notification(message)

    def _on_intent_set(self, intent: str) -> None:
        """Handle intent being set."""
        print(f"🎯 Intent: {intent}")

        if self._intent_checker:
            self._intent_checker.set_intent(intent)

    def _on_intent_clear(self) -> None:
        """Handle intent being cleared."""
        print("🎯 Intent cleared")

        if self._intent_checker:
            self._intent_checker.clear_intent()

    def _show_settings(self) -> None:
        """Show settings window."""
        if self._settings_window and self._root:
            self._root.after(0, self._settings_window.show)

    def _show_intent_bar(self) -> None:
        """Show intent input bar."""
        if self._intent_bar and self._root:
            current = ""
            if self._intent_checker:
                state = self._intent_checker.get_state()
                current = state.current_intent

            self._root.after(0, lambda: self._intent_bar.show(current))

    def _on_settings_save(self, settings: Settings) -> None:
        """Handle settings being saved."""
        print("⚙️ Settings saved")
        self.settings = settings

        # Update detector threshold
        if self._detector:
            self._detector.settings = settings

    def _toggle_pause(self) -> None:
        """Toggle monitoring pause."""
        if self._tray:
            if self._tray.is_paused:
                print("⏸️ Monitoring paused")
                self._update_widget_state("paused")
            else:
                print("▶️ Monitoring resumed")
                self._update_widget_state("active")

    def _quit(self) -> None:
        """Quit the application."""
        print("\n👋 Shutting down OpenSati...")

        self._running = False

        # Stop components
        if self._detector:
            self._detector.stop()

        if self._decompression:
            self._decompression.stop_monitoring()

        if self._intent_checker:
            self._intent_checker.stop()

        if self._tray:
            self._tray.stop()

        if self._grayscale and self._grayscale.is_active():
            self._grayscale.restore()

        # Destroy root window
        if self._root:
            self._root.quit()
            self._root.destroy()

        print("✅ Goodbye!")
        sys.exit(0)
