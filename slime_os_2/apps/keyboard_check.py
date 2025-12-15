"""
Keyboard Test App

Simple app for testing keyboard input by displaying raw keycodes.
Press any key to see its keycode value.
"""

from slime.app import App
from lib.keycode import Keycode


class KeyboardTestApp(App):
    """Keyboard Test - display raw keycodes"""

    name = "Keyboard Test"
    id = "keyboard_test"

    def __init__(self, system):
        super().__init__(system)
        self.key_history = []  # Store last pressed keys
        self.max_history = 15  # Max number of keys to display
        self.raw_mode = False  # Toggle for raw hex mode
        self.need_update = True

    def run(self):
        """Main app loop"""
        self.sys.log.info("Keyboard Test app starting")

        # Build list of all keycodes to check (for normal mode)
        all_keycodes = []
        for attr_name in dir(Keycode):
            if not attr_name.startswith('_'):
                keycode_value = getattr(Keycode, attr_name)
                if isinstance(keycode_value, int):
                    all_keycodes.append((attr_name, keycode_value))

        # Sort by keycode value for consistent ordering
        all_keycodes.sort(key=lambda x: x[1])

        # Build reverse lookup for raw mode
        keycode_to_name = {kc: name for name, kc in all_keycodes}

        while True:
            key_pressed = False

            if self.raw_mode:
                # RAW MODE - Read directly from keyboard driver
                if hasattr(self.sys.input, '_read_raw_data'):
                    raw_code = self.sys.input._read_raw_data()

                    if raw_code != 0:
                        # Got a key event
                        is_press = raw_code > 0
                        abs_code = abs(raw_code)

                        # Try to find if this is mapped
                        mapped_keycode = None
                        if hasattr(self.sys.input, 'KEY_MAP'):
                            mapped_keycode = self.sys.input.KEY_MAP.get(abs_code)

                        # Build display string
                        if mapped_keycode is not None:
                            keycode_name = keycode_to_name.get(mapped_keycode, f"KC_{mapped_keycode}")
                            display = f"{'PRESS' if is_press else 'RELEASE'}: 0x{abs_code:02X} -> {keycode_name}"
                        else:
                            display = f"{'PRESS' if is_press else 'RELEASE'}: 0x{abs_code:02X} (unmapped)"

                        self.key_history.append(("RAW", display))
                        if len(self.key_history) > self.max_history:
                            self.key_history.pop(0)
                        key_pressed = True
                else:
                    # Driver doesn't support raw mode
                    if not self.key_history or self.key_history[-1][0] != "ERROR":
                        self.key_history.append(("ERROR", "Raw mode not supported"))
                        key_pressed = True
            else:
                # NORMAL MODE - Check all keycodes
                for key_name, keycode_value in all_keycodes:
                    if self.sys.key_pressed(keycode_value):
                        # Add to history
                        self.key_history.append((key_name, hex(keycode_value)))
                        # Keep only max_history items
                        if len(self.key_history) > self.max_history:
                            self.key_history.pop(0)
                        key_pressed = True

            # Check for mode toggle (R key) - only in normal mode
            if not self.raw_mode and self.sys.key_pressed(Keycode.R):
                self.raw_mode = True
                self.key_history = []  # Clear history when switching modes
                self.need_update = True

            # Redraw if needed
            if key_pressed or self.need_update:
                self._draw_ui()
                self.need_update = False

            # Check for quit
            if self.sys.key_pressed(Keycode.ESCAPE):
                # In raw mode, use raw code check
                if self.raw_mode:
                    if hasattr(self.sys.input, 'inv_map'):
                        esc_raw = self.sys.input.inv_map.get(Keycode.ESCAPE)
                        if esc_raw and self.sys.input.held.get(esc_raw, False):
                            return
                else:
                    return

            yield

    def _draw_ui(self):
        """Draw keyboard test UI"""
        # Clear screen
        self.sys.clear((0, 16, 32))  # Dark blue background

        # Title with mode indicator
        title = "Keyboard Test"
        if self.raw_mode:
            title += " (RAW MODE)"
        self.sys.draw_text(title, 5, 5, scale=2, color=(255, 255, 0))

        y = 30

        # Instructions based on mode
        if self.raw_mode:
            self.sys.draw_text("Raw I2C codes from driver", 5, y, scale=1, color=(255, 128, 0))
            y += 12
            self.sys.draw_text("Press/Release shown with hex", 5, y, scale=1, color=(200, 200, 200))
            y += 12
            self.sys.draw_text("[Esc] Quit", 5, y, scale=1, color=(150, 150, 150))
        else:
            self.sys.draw_text("Press any key to see keycode", 5, y, scale=1, color=(200, 200, 200))
            y += 12
            self.sys.draw_text("[R] Raw Mode  [Esc] Quit", 5, y, scale=1, color=(150, 150, 150))

        # Draw history
        y += 20
        if self.key_history:
            header = "Raw codes:" if self.raw_mode else "Recent keys:"
            self.sys.draw_text(header, 5, y, scale=1, color=(0, 255, 255))
            y += 15

            for key_name, keycode_hex in self.key_history:
                if self.raw_mode:
                    # In raw mode, keycode_hex is actually the full display string
                    text = keycode_hex
                    # Truncate if too long
                    if len(text) > 48:
                        text = text[:45] + "..."

                    # Color code unmapped vs mapped
                    if "(unmapped)" in text:
                        text_color = (255, 128, 0)  # Orange for unmapped
                    else:
                        text_color = (0, 255, 0)  # Green for mapped
                else:
                    # Normal mode
                    display_name = key_name if len(key_name) <= 20 else key_name[:17] + "..."
                    text = f"{display_name}: {keycode_hex}"
                    text_color = (255, 255, 255)

                self.sys.draw_text(text, 10, y, scale=1, color=text_color)
                y += 12

                # Stop if we run out of space
                if y > self.sys.height - 20:
                    break
        else:
            wait_msg = "Press keys to see raw codes..." if self.raw_mode else "Waiting for keypress..."
            self.sys.draw_text(wait_msg, 10, y, scale=1, color=(150, 150, 150))

        # Update display
        self.sys.update()
