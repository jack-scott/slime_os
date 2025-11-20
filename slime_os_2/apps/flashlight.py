"""
Flashlight App

Simple app that toggles between white and black screen.
Demonstrates basic app structure and input handling.
"""

from slime.app import App
from lib.keycode import Keycode


class FlashlightApp(App):
    """Flashlight - toggle screen on/off"""

    name = "Flashlight"
    id = "flashlight"

    def run(self):
        """Main app loop"""
        self.sys.log.info("Flashlight starting")
        led_on = True  # Start with light on

        while True:
            # Draw UI based on state
            if led_on:
                # Light on - white screen
                self.sys.clear((255, 255, 255))
                self.sys.draw_text("FLASHLIGHT ON", 20, 20, scale=3, color=(0, 0, 0))
            else:
                # Light off - black screen
                self.sys.clear((0, 0, 0))
                self.sys.draw_text("FLASHLIGHT OFF", 20, 20, scale=3)

            # Draw controls
            self.sys.draw_text("[Enter] Toggle", 20, 100, scale=1, color=(128, 128, 128) if led_on else (255, 255, 255))
            self.sys.draw_text("[Q] Quit", 20, 120, scale=1, color=(128, 128, 128) if led_on else (255, 255, 255))

            # Update display
            self.sys.update()

            # Handle input
            keys = self.sys.keys_pressed([Keycode.ENTER, Keycode.Q])

            if keys[Keycode.ENTER]:
                # Toggle state
                led_on = not led_on

            if keys[Keycode.Q]:
                # Exit app (returns to launcher)
                return

            # Return control to OS
            yield
