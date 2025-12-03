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
        self.led_on = False  # Start with light on
        self.need_update = True

        # Pre-create string constants to avoid allocations in loop
        self.TEXT_ON = "FLASHLIGHT ON"
        self.TEXT_OFF = "FLASHLIGHT OFF"
        self.TEXT_TOGGLE = "[Enter] Toggle"
        self.TEXT_QUIT = "[Q] Quit"

        # Memory debugging - log every 60 frames
        frame_count = 0
        log_interval = 60

        while True:
            frame_count += 1

            # Log memory usage periodically
            if frame_count % log_interval == 0:
                import gc
                gc.collect()
                mem = self.sys.memory_info()
                self.sys.log.debug(f"Flashlight frame {frame_count}: {mem['free']//1024}KB free, {mem['percent_used']:.1f}% used")

            keys = self.sys.keys_pressed([Keycode.ENTER, Keycode.Q])
            # Check if any key was pressed
            if any(keys.values()):
                self.need_update = True

            if keys[Keycode.ENTER]:
                # Toggle state
                self.led_on = not self.led_on

            if keys[Keycode.Q]:
                # Exit app (returns to launcher)
                return

            # Handle input
            if self.need_update:
                self._draw_ui()
                self.sys.update()
                self.need_update = False

            # Return control to OS
            yield

    def _draw_ui(self):
        """Draw UI based on state"""
        if self.led_on:
            # Light on - white screen
            self.sys.clear((255, 255, 255))
            self.sys.draw_text(self.TEXT_ON, 20, 20, scale=3, color=(0, 0, 0))
            control_color = (128, 128, 128)
        else:
            # Light off - black screen
            self.sys.clear((0, 0, 0))
            self.sys.draw_text(self.TEXT_OFF, 20, 20, scale=3)
            control_color = (255, 255, 255)

        # Draw controls - reuse pre-created strings
        self.sys.draw_text(self.TEXT_TOGGLE, 20, 100, scale=1, color=control_color)
        self.sys.draw_text(self.TEXT_QUIT, 20, 120, scale=1, color=control_color)