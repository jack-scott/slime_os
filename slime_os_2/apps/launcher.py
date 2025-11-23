"""
Launcher - App Selector

Built-in app that displays available apps and lets user launch them.
This is the "home screen" of Slime OS.
"""

from slime.app import App
from lib.keycode import Keycode
import os


class Launcher(App):
    """
    Launcher - select and launch apps

    Future enhancements:
    - Settings page
    - About page
    - App icons
    - Categories
    """

    name = "Launcher"
    id = "launcher"

    def __init__(self, system):
        super().__init__(system)
        self.apps = []
        self.selected_index = 0
        self.need_update = True

    def discover_apps(self):
        """
        Discover available apps by scanning apps/ directory.

        Returns:
            List of app classes
        """
        apps = []

        # Get list of Python files in apps/ directory
        try:
            files = os.listdir('apps')
        except:
            files = []

        for filename in files:
            # Skip non-Python files and special files
            if not filename.endswith('.py'):
                continue
            if filename.startswith('_'):
                continue
            if filename == 'launcher.py':
                continue  # Don't list launcher itself

            # Try to import the app
            module_name = filename[:-3]  # Remove .py
            try:
                # Dynamic import
                # MicroPython's __import__ doesn't accept keyword arguments
                module = __import__(f'apps.{module_name}', None, None, ['*'])

                # Look for App class that's actually an App subclass
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, App) and
                        attr != App and
                        hasattr(attr, 'name') and
                        hasattr(attr, 'id')):
                        apps.append(attr)
                        break

            except Exception as e:
                print(f"[Launcher] Failed to import {module_name}: {e}")

        # Sort by name
        apps.sort(key=lambda app: app.name)

        return apps

    def run(self):
        """Main launcher loop"""
        # Discover available apps
        self.sys.log.info("Launcher: Discovering apps")
        self.apps = self.discover_apps()
        self.sys.log.info(f"Launcher: Found {len(self.apps)} apps")

        # Handle case of no apps
        if not self.apps:
            self.sys.log.warn("Launcher: No apps found")
            while True:
                self.sys.clear((128, 0, 0))  # Red
                self.sys.draw_text("NO APPS FOUND", 20, 20, scale=2)
                self.sys.draw_text("Add apps to apps/", 20, 60)
                self.sys.update()
                yield

        # Main loop
        self.sys.log.debug("Launcher: Entering main loop")
        while True:
            # Draw UI
            if self.need_update:
                self._draw_ui()
                self.need_update = False

            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.UP_ARROW,
                Keycode.DOWN_ARROW,
                Keycode.ENTER
            ])

            # Check if any key was pressed
            if any(keys.values()):
                self.need_update = True

            if keys[Keycode.UP_ARROW]:
                # Move selection up
                self.selected_index = self.selected_index - 1
                # wrap around if at the top
                if self.selected_index < 0:
                    self.selected_index = len(self.apps) - 1

            if keys[Keycode.DOWN_ARROW]:
                # Move selection down
                self.selected_index = self.selected_index + 1
                # wrap around if at the bottom
                if self.selected_index >= len(self.apps):
                    self.selected_index = 0

            if keys[Keycode.ENTER]:
                # Launch selected app
                selected_app = self.apps[self.selected_index]
                self.sys.log.debug(f"Launcher: Launching {selected_app.name}")
                return ('launch', selected_app)

            yield

    def _draw_ui(self):
        """Draw launcher UI"""
        # Clear screen
        self.sys.clear((0, 0, 64))  # Dark blue background

        # Draw title
        self.sys.draw_text("SLIME OS", 10, 10, scale=2, color=(255, 255, 0))

        # Draw device name and memory
        mem = self.sys.memory_info()
        mem_text = f"{mem['free']//1024}KB free"
        self.sys.draw_text(self.sys.device.name, 10, 40, scale=1, color=(200, 200, 200))
        self.sys.draw_text(mem_text, 10, 55, scale=1, color=(200, 200, 200))

        # Draw app list
        y = 80
        for i, app in enumerate(self.apps):
            if i == self.selected_index:
                # Selected app - highlight
                self.sys.draw_rect(5, y - 2, self.sys.width - 10, 16, (255, 255, 0))
                color = (0, 0, 0)  # Black text on yellow
            else:
                # Normal app
                color = (255, 255, 255)  # White text

            # Draw app name
            self.sys.draw_text(f"> {app.name}", 10, y, scale=1, color=color)

            y += 20

            # Stop if we run out of space
            if y > self.sys.height - 60:
                break

        # Draw instructions at bottom
        instructions_y = self.sys.height - 40
        self.sys.draw_text("[Up/Down] Select", 10, instructions_y, scale=1, color=(200, 200, 200))
        self.sys.draw_text("[Enter] Launch", 10, instructions_y + 15, scale=1, color=(200, 200, 200))

        # Update display
        self.sys.update()
