"""
Ollama setup and auto-installation.

Handles checking for Ollama and installing it if missing.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable


@dataclass
class OllamaSetup:
    """
    Handles Ollama installation and setup.
    
    Auto-installs on macOS/Linux using official script.
    Prompts user on Windows.
    """
    
    on_log: Callable[[str], None] | None = None
    
    def is_installed(self) -> bool:
        """Check if Ollama is installed."""
        return shutil.which("ollama") is not None
    
    def is_running(self) -> bool:
        """Check if Ollama server is running."""
        try:
            import ollama
            ollama.list()
            return True
        except Exception:
            return False
    
    def install(self) -> bool:
        """
        Install Ollama if not present.
        
        Returns True if installation succeeded or already installed.
        """
        if self.is_installed():
            self._log("✅ Ollama already installed")
            return True
        
        system = platform.system()
        
        if system == "Darwin" or system == "Linux":
            return self._install_unix()
        elif system == "Windows":
            return self._install_windows()
        else:
            self._log(f"⚠️ Unsupported OS: {system}")
            return False
    
    def _install_unix(self) -> bool:
        """Install Ollama on macOS/Linux using official script."""
        self._log("📦 Installing Ollama...")
        
        try:
            # Run official install script
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.com/install.sh"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self._log("⚠️ Failed to download Ollama installer")
                return False
            
            # Pipe to sh
            install_result = subprocess.run(
                ["sh"],
                input=result.stdout,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if install_result.returncode == 0:
                self._log("✅ Ollama installed successfully")
                return True
            else:
                self._log(f"⚠️ Installation failed: {install_result.stderr[:100]}")
                return False
                
        except subprocess.TimeoutExpired:
            self._log("⚠️ Installation timed out")
            return False
        except Exception as e:
            self._log(f"⚠️ Installation error: {e}")
            return False
    
    def _install_windows(self) -> bool:
        """Prompt user to install Ollama on Windows."""
        self._log("📦 Ollama not found. Please install from: https://ollama.com/download")
        
        # Try to open download page
        try:
            import webbrowser
            webbrowser.open("https://ollama.com/download/windows")
            self._log("🌐 Opened download page in browser")
        except Exception:
            pass
        
        return False
    
    def ensure_model(self, model_name: str = "llava") -> bool:
        """
        Ensure a model is pulled.
        
        Returns True if model is available.
        """
        if not self.is_installed():
            return False
        
        try:
            import ollama
            
            # Check if model exists
            models = ollama.list()
            available = [m.get("name", "") for m in models.get("models", [])]
            
            if any(model_name in m for m in available):
                self._log(f"✅ Model {model_name} ready")
                return True
            
            # Pull model
            self._log(f"📥 Pulling {model_name} model...")
            ollama.pull(model_name)
            self._log(f"✅ Model {model_name} downloaded")
            return True
            
        except Exception as e:
            self._log(f"⚠️ Model setup failed: {e}")
            return False
    
    def start_server(self) -> bool:
        """Start Ollama server if not running."""
        if self.is_running():
            return True
        
        self._log("🚀 Starting Ollama server...")
        
        try:
            # Start in background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Wait for server to be ready
            import time
            for _ in range(10):
                time.sleep(1)
                if self.is_running():
                    self._log("✅ Ollama server started")
                    return True
            
            self._log("⚠️ Server didn't start in time")
            return False
            
        except Exception as e:
            self._log(f"⚠️ Failed to start server: {e}")
            return False
    
    def _log(self, message: str):
        """Log message."""
        if self.on_log:
            self.on_log(message)
        else:
            print(message)
