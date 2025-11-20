"""
Slime OS 2 - Main Entry Point

This is the entry point for Slime OS 2.
It loads the device configuration, initializes the system, and boots the launcher.

Usage:
    1. Edit config.py to select your device
    2. Upload all files to your device
    3. Run main.py (or configure device to run it on boot)
"""

from config import DEVICE, WATCHDOG_TIMEOUT
from slime.devices import get_device
from slime.system import System
from apps.launcher import Launcher


def main():
    """Main entry point"""
    print("=" * 40)
    print("Slime OS 2")
    print("=" * 40)

    # Load device configuration
    print(f"Loading device: {DEVICE}")
    try:
        device = get_device(DEVICE)
        print(f"Device: {device.name}")
    except Exception as e:
        print(f"ERROR: Failed to load device '{DEVICE}': {e}")
        return

    # Create system
    print("Initializing system...")
    system = System(device, watchdog_timeout=WATCHDOG_TIMEOUT)

    # Boot with launcher
    print("Booting...")
    print("=" * 40)
    system.boot(Launcher)


if __name__ == '__main__':
    main()
