#!/usr/bin/env python3
"""
Build OpenSati standalone executables using PyInstaller.

Run: python scripts/build.py
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def main():
    """Build standalone executable."""
    # Force UTF-8 output for Windows Unicode support
    if sys.stdout.encoding.lower() != 'utf-8':
        try:
             sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass  # Fallback if reconfigure fails

    print("\n🔨 Building OpenSati Standalone Executable")
    print("=" * 50)

    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Platform-specific settings
    system = platform.system()

    if system == "Darwin":
        icon = "resources/icon.icns" if Path("resources/icon.icns").exists() else None
        name = "OpenSati"
        extra_args = ["--windowed", "--osx-bundle-identifier", "com.opensati.app"]
    elif system == "Windows":
        icon = "resources/icon.ico" if Path("resources/icon.ico").exists() else None
        name = "OpenSati"
        extra_args = ["--windowed"]
    else:  # Linux
        icon = "resources/icon.png" if Path("resources/icon.png").exists() else None
        name = "opensati"
        extra_args = []

    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", name,
        "--onefile",
        "--clean",
        "--noconfirm",
        "--add-data", f"config.yaml{os.pathsep}.",
    ]

    # Add icon if exists
    if icon and Path(icon).exists():
        cmd.extend(["--icon", icon])

    # Add platform-specific args
    cmd.extend(extra_args)

    # Add entry point
    cmd.append("src/opensati/__main__.py")

    print(f"\n🔧 Running: {' '.join(cmd)}")
    print()

    # Run PyInstaller
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n✅ Build complete!")
        print(f"   Output: dist/{name}")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
