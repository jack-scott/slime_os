#!/usr/bin/env python3
"""
Slime OS 2 Simulator Runner

Run Slime OS locally on your desktop computer for rapid development.

Usage:
    python run_simulator.py
    python run_simulator.py --watch    # Enable hot-reload
    python run_simulator.py --help     # Show help

Requirements:
    pip install pygame
    pip install watchdog  # Optional, for hot-reload
"""

import sys
import os
import argparse

# Set up paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # dev/
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)  # slime_os_2/

# Change to project directory so relative paths (like 'apps/') work correctly
os.chdir(PROJECT_DIR)

# Add project directory to path FIRST (for apps, slime, lib, config)
sys.path.insert(0, PROJECT_DIR)

# Add compat directory to path (for hardware stubs like machine, st7789, etc.)
COMPAT_DIR = os.path.join(SCRIPT_DIR, 'compat')
sys.path.insert(0, COMPAT_DIR)

# Now we can import the rest
from config import DEVICE
from slime.devices import get_device
from slime.system import System
from apps.launcher import Launcher


def run_simulator():
    """Run the simulator"""
    print("=" * 60)
    print("Slime OS 2 - Simulator")
    print("=" * 60)

    # Verify device is set to simulator
    device = "simulator"

    # Load device
    print(f"Loading device: {device}")
    try:
        device = get_device(device)
        print(f"Device: {device.name}")
    except Exception as e:
        print(f"ERROR: Failed to load device '{device}': {e}")
        return

    # Create system
    print("Initializing system...")
    system = System(device, watchdog_timeout=None)  # No watchdog in simulator

    # Boot with launcher
    print("Booting...")
    print("=" * 60)
    print()

    try:
        system.boot(Launcher)
    except SystemExit as e:
        print(f"\n{e}")
    except KeyboardInterrupt:
        print("\nSimulator stopped by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup pygame
        try:
            import pygame
            pygame.quit()
        except:
            pass
        print("\nSimulator exited")


def watch_and_reload():
    """Run simulator with hot-reload support"""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        import time
        import subprocess
    except ImportError:
        print("ERROR: watchdog not installed")
        print("Install with: pip install watchdog")
        return

    class ReloadHandler(FileSystemEventHandler):
        """Handler for file changes"""

        def __init__(self):
            self.last_reload = 0
            self.process = None

        def start_simulator(self):
            """Start simulator process"""
            if self.process:
                self.process.terminate()
                self.process.wait()

            print("\n" + "=" * 60)
            print("Starting simulator...")
            print("=" * 60 + "\n")

            self.process = subprocess.Popen([sys.executable, __file__])

        def on_modified(self, event):
            """Handle file modification"""
            # Only reload for Python files
            if not event.src_path.endswith('.py'):
                return

            # Debounce (wait 1 second between reloads)
            now = time.time()
            if now - self.last_reload < 1.0:
                return

            self.last_reload = now

            print(f"\n[Hot Reload] File changed: {event.src_path}")
            self.start_simulator()

    print("=" * 60)
    print("Slime OS 2 - Simulator (Hot Reload Enabled)")
    print("=" * 60)
    print("Watching for file changes...")
    print("Press Ctrl+C to stop")
    print()

    handler = ReloadHandler()
    handler.start_simulator()

    observer = Observer()
    observer.schedule(handler, SCRIPT_DIR, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        observer.stop()
        if handler.process:
            handler.process.terminate()
    observer.join()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Slime OS 2 Simulator - Run on desktop for development'
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Enable hot-reload (restart on file changes)'
    )

    args = parser.parse_args()

    if args.watch:
        watch_and_reload()
    else:
        run_simulator()


if __name__ == '__main__':
    main()
