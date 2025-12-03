"""
CPU Manager App

View and adjust CPU frequency on the RP2350.
Allows overclocking or underclocking for performance vs power trade-offs.
"""

from slime.app import App
from lib.keycode import Keycode


class CPUManagerApp(App):
    """CPU Manager - view and set CPU frequency"""

    name = "CPU Manager"
    id = "cpu_manager"

    # Available frequency presets (in MHz)
    FREQ_PRESETS = [
        (50, "Ultra Low Power", "Slowest, saves power"),
        (125, "RP2040 Default", "Standard RP2040 speed"),
        (133, "Standard", "Common clock speed"),
        (150, "RP2350 Default", "RP2350 standard"),
        (200, "Fast", "Faster, stable"),
        (250, "Maximum", "Overclocked, may be unstable"),
    ]

    def __init__(self, system):
        super().__init__(system)
        self.selected_index = 3  # Default to 150MHz
        self.current_freq_mhz = 0
        self.need_update = True
        self.status_message = ""
        self.status_timer = 0

    def get_current_frequency(self):
        """Get current CPU frequency in MHz"""
        try:
            import machine
            freq_hz = machine.freq()
            return freq_hz // 1_000_000
        except Exception as e:
            self.sys.log.error(f"CPU: Failed to get frequency: {e}")
            return 0

    def set_frequency(self, freq_mhz):
        """Set CPU frequency"""
        try:
            import machine
            freq_hz = freq_mhz * 1_000_000
            machine.freq(freq_hz)
            self.sys.log.info(f"CPU: Set frequency to {freq_mhz} MHz")
            self.status_message = f"Set to {freq_mhz} MHz"
            self.status_timer = 60  # Show for 2 seconds at 30 FPS
            return True
        except Exception as e:
            self.sys.log.error(f"CPU: Failed to set frequency: {e}")
            self.status_message = f"Error: {str(e)}"
            self.status_timer = 90  # Show for 3 seconds
            return False

    def run(self):
        """Main app loop"""
        self.sys.log.info("CPU Manager starting")

        # Get initial frequency
        self.current_freq_mhz = self.get_current_frequency()

        # Find closest preset to current frequency
        for i, (freq, _, _) in enumerate(self.FREQ_PRESETS):
            if abs(freq - self.current_freq_mhz) < 10:  # Within 10 MHz
                self.selected_index = i
                break

        self.need_update = True

        while True:
            # Update current frequency periodically
            if self.status_timer == 0:
                self.current_freq_mhz = self.get_current_frequency()

            # Decrement status timer
            if self.status_timer > 0:
                self.status_timer -= 1
                if self.status_timer == 0:
                    self.need_update = True

            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.UP_ARROW,
                Keycode.DOWN_ARROW,
                Keycode.ENTER,
                Keycode.Q
            ])

            if keys[Keycode.UP_ARROW]:
                # Move selection up
                if self.selected_index > 0:
                    self.selected_index -= 1
                    self.need_update = True

            if keys[Keycode.DOWN_ARROW]:
                # Move selection down
                if self.selected_index < len(self.FREQ_PRESETS) - 1:
                    self.selected_index += 1
                    self.need_update = True

            if keys[Keycode.ENTER]:
                # Apply selected frequency
                freq_mhz = self.FREQ_PRESETS[self.selected_index][0]
                self.set_frequency(freq_mhz)
                self.current_freq_mhz = self.get_current_frequency()
                self.need_update = True

            if keys[Keycode.Q]:
                # Exit
                return

            # Draw UI if needed
            if self.need_update:
                self._draw_ui()
                self.need_update = False

            yield

    def _draw_ui(self):
        """Draw CPU manager UI"""
        # Clear screen
        self.sys.clear((0, 32, 0))  # Dark green background

        # Title
        self.sys.draw_text("CPU Manager", 5, 5, scale=2, color=(255, 255, 0))

        # Current frequency
        y = 30
        self.sys.draw_text("Current Frequency:", 5, y, scale=1, color=(200, 200, 200))
        y += 15
        self.sys.draw_text(f"{self.current_freq_mhz} MHz", 5, y, scale=2, color=(0, 255, 0))
        y += 25

        # Separator
        self.sys.draw_rect(0, y, self.sys.width, 1, (100, 100, 100))
        y += 5

        # Frequency presets
        self.sys.draw_text("Select Frequency:", 5, y, scale=1, color=(255, 255, 0))
        y += 15

        for i, (freq_mhz, name, desc) in enumerate(self.FREQ_PRESETS):
            is_selected = (i == self.selected_index)
            is_current = (abs(freq_mhz - self.current_freq_mhz) < 10)

            # Highlight selected
            if is_selected:
                self.sys.draw_rect(2, y - 2, self.sys.width - 4, 28, (255, 255, 0))
                text_color = (0, 0, 0)
            else:
                text_color = (255, 255, 255)

            # Show current frequency indicator
            prefix = "* " if is_current else "  "

            # Draw preset
            self.sys.draw_text(f"{prefix}{freq_mhz} MHz - {name}", 5, y, scale=1, color=text_color)
            y += 12
            self.sys.draw_text(f"  {desc}", 5, y, scale=1, color=text_color if is_selected else (150, 150, 150))
            y += 18

            # Stop if running out of space
            if y > self.sys.height - 50:
                break

        # Status message
        if self.status_timer > 0:
            status_y = self.sys.height - 50
            self.sys.draw_rect(0, status_y - 2, self.sys.width, 16, (0, 100, 0))
            self.sys.draw_text(self.status_message, 5, status_y, scale=1, color=(255, 255, 255))

        # Controls at bottom
        controls_y = self.sys.height - 30
        self.sys.draw_text("[Up/Down] Select", 5, controls_y, scale=1, color=(150, 150, 150))
        controls_y += 12
        self.sys.draw_text("[Enter] Apply  [Q] Quit", 5, controls_y, scale=1, color=(150, 150, 150))

        # Update display
        self.sys.update()
