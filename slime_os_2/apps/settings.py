"""
Settings App

Configure system settings:
- CPU Frequency
- Display Brightness
- Keyboard Brightness

All settings are automatically saved and persist across reboots.
"""

from slime.app import App
from lib.keycode import Keycode


class SettingsApp(App):
    """Settings configuration app"""

    name = "Settings"
    id = "settings"

    # CPU frequency presets (in MHz)
    CPU_PRESETS = [50, 100, 125, 133, 150, 175, 200, 225, 250]

    def __init__(self, system):
        super().__init__(system)
        self.selected_index = 0  # Which setting is selected
        self.setting_names = ["CPU Frequency", "Display Brightness", "Keyboard Brightness"]

        # Load current values
        self.cpu_freq = self.sys.settings.get('cpu_freq_mhz', 150)
        self.display_brightness = self.sys.settings.get('display_brightness', 100)
        self.keyboard_brightness = self.sys.settings.get('keyboard_brightness', 50)

        self.need_update = True
        self.status_message = ""
        self.status_timer = 0

    def run(self):
        """Main settings loop"""
        self.sys.log.info("Settings app starting")
        self.need_update = True

        while True:
            # Decrement status timer
            if self.status_timer > 0:
                self.status_timer -= 1
                if self.status_timer == 0:
                    self.status_message = ""
                    self.need_update = True

            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.UP_ARROW,
                Keycode.DOWN_ARROW,
                Keycode.LEFT_ARROW,
                Keycode.RIGHT_ARROW,
                Keycode.ENTER,
                Keycode.Q,
                Keycode.S
            ])

            if keys[Keycode.UP_ARROW]:
                # Move selection up
                if self.selected_index > 0:
                    self.selected_index -= 1
                    self.need_update = True

            if keys[Keycode.DOWN_ARROW]:
                # Move selection down
                if self.selected_index < len(self.setting_names) - 1:
                    self.selected_index += 1
                    self.need_update = True

            if keys[Keycode.LEFT_ARROW]:
                # Decrease value
                if self._adjust_value(-1):
                    self.need_update = True

            if keys[Keycode.RIGHT_ARROW]:
                # Increase value
                if self._adjust_value(1):
                    self.need_update = True

            if keys[Keycode.S]:
                # Save settings
                self._save_settings()
                self.need_update = True

            if keys[Keycode.Q]:
                # Exit (without saving if not explicitly saved)
                return

            # Draw UI if needed
            if self.need_update:
                self._draw_ui()
                self.need_update = False

            yield

    def _adjust_value(self, delta):
        """
        Adjust the currently selected setting

        Args:
            delta: Amount to change (+1 or -1)

        Returns:
            True if value changed
        """
        if self.selected_index == 0:
            # CPU Frequency
            try:
                current_idx = self.CPU_PRESETS.index(self.cpu_freq)
            except ValueError:
                # Find closest preset
                current_idx = min(range(len(self.CPU_PRESETS)),
                                key=lambda i: abs(self.CPU_PRESETS[i] - self.cpu_freq))

            new_idx = current_idx + delta
            if 0 <= new_idx < len(self.CPU_PRESETS):
                self.cpu_freq = self.CPU_PRESETS[new_idx]
                self.sys.set_cpu_frequency(self.cpu_freq)
                self.status_message = f"CPU: {self.cpu_freq} MHz"
                self.status_timer = 60  # 2 seconds at 30 FPS
                return True

        elif self.selected_index == 1:
            # Display Brightness (0-255)
            new_val = self.display_brightness + (delta * 10)
            new_val = max(0, min(255, new_val))
            if new_val != self.display_brightness:
                self.display_brightness = new_val
                self.sys.set_display_brightness(self.display_brightness)
                self.status_message = f"Display: {self.display_brightness}"
                self.status_timer = 60
                return True

        elif self.selected_index == 2:
            # Keyboard Brightness (0-255)
            new_val = self.keyboard_brightness + (delta * 10)
            new_val = max(0, min(255, new_val))
            if new_val != self.keyboard_brightness:
                self.keyboard_brightness = new_val
                self.sys.set_keyboard_brightness(self.keyboard_brightness)
                self.status_message = f"Keyboard: {self.keyboard_brightness}"
                self.status_timer = 60
                return True

        return False

    def _save_settings(self):
        """Save all settings to disk"""
        # Update settings manager
        self.sys.settings.set('cpu_freq_mhz', self.cpu_freq)
        self.sys.settings.set('display_brightness', self.display_brightness)
        self.sys.settings.set('keyboard_brightness', self.keyboard_brightness)

        # Save to disk
        if self.sys.settings.save():
            self.status_message = "Settings saved!"
            self.sys.log.info("Settings saved to disk")
        else:
            self.status_message = "Save failed!"
            self.sys.log.error("Failed to save settings")

        self.status_timer = 90  # 3 seconds

    def _draw_ui(self):
        """Draw settings UI"""
        # Clear screen
        self.sys.clear((0, 0, 64))  # Dark blue background

        # Title
        self.sys.draw_text("Settings", 5, 5, scale=2, color=(255, 255, 0))

        y = 35

        # Draw each setting
        for i, name in enumerate(self.setting_names):
            is_selected = (i == self.selected_index)

            # Get current value
            if i == 0:
                value_text = f"{self.cpu_freq} MHz"
            elif i == 1:
                value_text = f"{self.display_brightness}"
            elif i == 2:
                value_text = f"{self.keyboard_brightness}"

            # Draw setting box
            box_height = 45
            if is_selected:
                # Selected - yellow box
                self.sys.draw_rect(3, y - 2, self.sys.width - 6, box_height, (255, 255, 0))
                name_color = (0, 0, 0)
                value_color = (0, 0, 128)
                bar_color = (0, 0, 255)
            else:
                # Not selected - dark box
                self.sys.draw_rect(3, y - 2, self.sys.width - 6, box_height, (32, 32, 64))
                name_color = (255, 255, 255)
                value_color = (0, 255, 0)
                bar_color = (0, 128, 0)

            # Draw setting name
            self.sys.draw_text(name, 8, y + 2, scale=1, color=name_color)

            # Draw value
            self.sys.draw_text(value_text, 8, y + 15, scale=1, color=value_color)

            # Draw visual bar
            if i == 0:
                # CPU frequency bar (50-250 MHz range)
                max_val = 250
                min_val = 50
                bar_width = int((self.cpu_freq - min_val) / (max_val - min_val) * (self.sys.width - 20))
            elif i == 1:
                # Display brightness bar (0-255)
                bar_width = int(self.display_brightness / 255 * (self.sys.width - 20))
            elif i == 2:
                # Keyboard brightness bar (0-255)
                bar_width = int(self.keyboard_brightness / 255 * (self.sys.width - 20))

            bar_width = max(2, bar_width)  # Minimum 2 pixels
            self.sys.draw_rect(8, y + 30, bar_width, 8, bar_color)

            y += box_height + 8

        # Status message
        if self.status_message:
            status_y = self.sys.height - 50
            self.sys.draw_rect(0, status_y - 2, self.sys.width, 16, (0, 128, 0))
            self.sys.draw_text(self.status_message, 5, status_y, scale=1, color=(255, 255, 255))

        # Controls at bottom
        controls_y = self.sys.height - 30
        self.sys.draw_text("[Up/Down] Select", 5, controls_y, scale=1, color=(150, 150, 150))
        controls_y += 12
        self.sys.draw_text("[Left/Right] Adjust  [S] Save  [Q] Quit", 5, controls_y, scale=1, color=(150, 150, 150))

        # Update display
        self.sys.update()
