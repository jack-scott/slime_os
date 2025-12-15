"""
WiFi Configuration App

Configure WiFi credentials and test connection.
Type SSID and password using the keyboard, then save to settings.
"""

from slime.app import App
from lib.keycode import Keycode


class WiFiConfigApp(App):
    """WiFi Configuration - set WiFi credentials"""

    name = "WiFi Config"
    id = "wifi_config"

    # Keycode to character mapping
    KEYCODE_TO_CHAR = {
        # Lowercase letters
        Keycode.A: 'a', Keycode.B: 'b', Keycode.C: 'c', Keycode.D: 'd',
        Keycode.E: 'e', Keycode.F: 'f', Keycode.G: 'g', Keycode.H: 'h',
        Keycode.I: 'i', Keycode.J: 'j', Keycode.K: 'k', Keycode.L: 'l',
        Keycode.M: 'm', Keycode.N: 'n', Keycode.O: 'o', Keycode.P: 'p',
        Keycode.Q: 'q', Keycode.R: 'r', Keycode.S: 's', Keycode.T: 't',
        Keycode.U: 'u', Keycode.V: 'v', Keycode.W: 'w', Keycode.X: 'x',
        Keycode.Y: 'y', Keycode.Z: 'z',
        # Uppercase letters
        Keycode.A_UPPER: 'A', Keycode.B_UPPER: 'B', Keycode.C_UPPER: 'C', Keycode.D_UPPER: 'D',
        Keycode.E_UPPER: 'E', Keycode.F_UPPER: 'F', Keycode.G_UPPER: 'G', Keycode.H_UPPER: 'H',
        Keycode.I_UPPER: 'I', Keycode.J_UPPER: 'J', Keycode.K_UPPER: 'K', Keycode.L_UPPER: 'L',
        Keycode.M_UPPER: 'M', Keycode.N_UPPER: 'N', Keycode.O_UPPER: 'O', Keycode.P_UPPER: 'P',
        Keycode.Q_UPPER: 'Q', Keycode.R_UPPER: 'R', Keycode.S_UPPER: 'S', Keycode.T_UPPER: 'T',
        Keycode.U_UPPER: 'U', Keycode.V_UPPER: 'V', Keycode.W_UPPER: 'W', Keycode.X_UPPER: 'X',
        Keycode.Y_UPPER: 'Y', Keycode.Z_UPPER: 'Z',
        # Numbers
        Keycode.ZERO: '0', Keycode.ONE: '1', Keycode.TWO: '2', Keycode.THREE: '3',
        Keycode.FOUR: '4', Keycode.FIVE: '5', Keycode.SIX: '6', Keycode.SEVEN: '7',
        Keycode.EIGHT: '8', Keycode.NINE: '9',
        # Special characters
        Keycode.SPACE: ' ',
        Keycode.MINUS: '-',
        Keycode.PERIOD: '.',
        Keycode.COMMA: ',',
        Keycode.FORWARD_SLASH: '/',
        Keycode.BACKSLASH: '\\',
        Keycode.SEMICOLON: ';',
        Keycode.QUOTE: "'",
        Keycode.LEFT_BRACKET: '[',
        Keycode.RIGHT_BRACKET: ']',
        Keycode.EQUALS: '=',
        Keycode.GRAVE_ACCENT: '`',
    }

    # Uppercase keycodes set for fast lookup (created once as class constant)
    _UPPERCASE_KEYCODES = {
        Keycode.A_UPPER, Keycode.B_UPPER, Keycode.C_UPPER, Keycode.D_UPPER,
        Keycode.E_UPPER, Keycode.F_UPPER, Keycode.G_UPPER, Keycode.H_UPPER,
        Keycode.I_UPPER, Keycode.J_UPPER, Keycode.K_UPPER, Keycode.L_UPPER,
        Keycode.M_UPPER, Keycode.N_UPPER, Keycode.O_UPPER, Keycode.P_UPPER,
        Keycode.Q_UPPER, Keycode.R_UPPER, Keycode.S_UPPER, Keycode.T_UPPER,
        Keycode.U_UPPER, Keycode.V_UPPER, Keycode.W_UPPER, Keycode.X_UPPER,
        Keycode.Y_UPPER, Keycode.Z_UPPER,
    }

    def __init__(self, system):
        super().__init__(system)
        self.ssid = self.sys.settings.get('wifi_ssid', '')
        self.password = self.sys.settings.get('wifi_password', '')
        self.auto_connect = self.sys.settings.get('wifi_auto_connect', True)
        self.selected_index = 0
        self.editing = False
        self.need_update = True
        self.status_message = ""
        self.status_timer = 0

        # Pre-build list of all keycodes to check (created once)
        control_keys = [Keycode.BACKSPACE, Keycode.ENTER, Keycode.ESCAPE]
        modifier_keys = [Keycode.LEFT_SHIFT, Keycode.RIGHT_SHIFT]
        self._all_keys_to_check = control_keys + modifier_keys + list(self.KEYCODE_TO_CHAR.keys())

        # Field names
        self.fields = ["SSID", "Password", "Auto-Connect"]

    def run(self):
        """Main app loop"""
        self.sys.log.info("WiFi Config app starting")
        self.need_update = True

        while True:
            # Decrement status timer
            if self.status_timer > 0:
                self.status_timer -= 1
                if self.status_timer == 0:
                    self.status_message = ""
                    self.need_update = True

            # Handle input
            if self.editing:
                # Editing mode - capture all keyboard input
                # Use pre-built list of keycodes (created once in __init__)
                # Use case_sensitive=True to get exact keycode matches for proper character mapping
                keys = self.sys.keys_pressed(self._all_keys_to_check, case_sensitive=True)

                # Check if shift is pressed
                shift_pressed = keys.get(Keycode.LEFT_SHIFT, False) or keys.get(Keycode.RIGHT_SHIFT, False)

                # Check control keys first
                if keys.get(Keycode.BACKSPACE, False):
                    if self.selected_index == 0 and len(self.ssid) > 0:
                        self.ssid = self.ssid[:-1]
                        self.need_update = True
                    elif self.selected_index == 1 and len(self.password) > 0:
                        self.password = self.password[:-1]
                        self.need_update = True

                elif keys.get(Keycode.ENTER, False):
                    self.editing = False
                    self.need_update = True

                elif keys.get(Keycode.ESCAPE, False):
                    self.editing = False
                    self.need_update = True

                else:
                    # Check character keys - iterate through KEYCODE_TO_CHAR once
                    # Uppercase keycodes are already in KEYCODE_TO_CHAR, so they'll be checked naturally
                    for keycode, char in self.KEYCODE_TO_CHAR.items():
                        if keys.get(keycode, False):
                            # Apply shift transformations for non-letter characters only
                            # (Letters are handled by caps lock via uppercase keycodes)
                            if shift_pressed and keycode not in self._UPPERCASE_KEYCODES:
                                # For numbers and symbols, shift changes the character
                                shift_map = {
                                    '0': ')', '1': '!', '2': '@', '3': '#', '4': '$',
                                    '5': '%', '6': '^', '7': '&', '8': '*', '9': '(',
                                    '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
                                    ';': ':', "'": '"', ',': '<', '.': '>', '/': '?',
                                    '`': '~'
                                }
                                char = shift_map.get(char, char)

                            if self.selected_index == 0:
                                self.ssid += char
                                self.need_update = True
                            elif self.selected_index == 1:
                                self.password += char
                                self.need_update = True
                            break  # Only process one key per frame

            else:
                # Navigation mode
                keys = self.sys.keys_pressed([
                    Keycode.UP_ARROW,
                    Keycode.DOWN_ARROW,
                    Keycode.ENTER,
                    Keycode.T,  # Test connection
                    Keycode.S,  # Save (can't use S in nav mode since it's a letter)
                    Keycode.C,  # Clear
                    Keycode.ESCAPE  # Quit
                ])

                if keys[Keycode.UP_ARROW]:
                    if self.selected_index > 0:
                        self.selected_index -= 1
                        self.need_update = True

                if keys[Keycode.DOWN_ARROW]:
                    if self.selected_index < len(self.fields) - 1:
                        self.selected_index += 1
                        self.need_update = True

                if keys[Keycode.ENTER]:
                    # Toggle auto-connect or enter edit mode
                    if self.selected_index == 2:
                        self.auto_connect = not self.auto_connect
                        self.need_update = True
                    else:
                        self.editing = True
                        self.need_update = True

                if keys[Keycode.C]:
                    # Clear current field
                    if self.selected_index == 0:
                        self.ssid = ""
                        self.status_message = "SSID cleared"
                    elif self.selected_index == 1:
                        self.password = ""
                        self.status_message = "Password cleared"
                    self.status_timer = 60
                    self.need_update = True

                if keys[Keycode.T]:
                    # Test connection
                    if not self.ssid:
                        self.status_message = "SSID is empty!"
                        self.status_timer = 90
                        self.need_update = True
                    else:
                        self.status_message = "Connecting..."
                        self.need_update = True
                        self._draw_ui()  # Show immediately

                        success, ip, error = self.sys.wifi_connect(self.ssid, self.password, timeout=15)
                        if success:
                            self.status_message = f"Success! IP: {ip}"
                        else:
                            self.status_message = f"Failed: {error}"
                        self.status_timer = 150  # Show for 5 seconds
                        self.need_update = True

                # Use F1 for save (since S is used for typing)
                if self.sys.key_pressed(Keycode.F1):
                    # Save settings
                    self.sys.settings.set('wifi_ssid', self.ssid)
                    self.sys.settings.set('wifi_password', self.password)
                    self.sys.settings.set('wifi_auto_connect', self.auto_connect)

                    if self.sys.settings.save():
                        self.status_message = "Settings saved!"
                    else:
                        self.status_message = "Save failed!"
                    self.status_timer = 90
                    self.need_update = True

                if keys[Keycode.ESCAPE]:
                    return

            # Draw UI if needed
            if self.need_update:
                self._draw_ui()
                self.need_update = False

            yield

    def _draw_ui(self):
        """Draw WiFi config UI"""
        # Clear screen
        self.sys.clear((16, 0, 48))  # Dark purple background

        # Title
        self.sys.draw_text("WiFi Config", 5, 5, scale=2, color=(255, 255, 0))

        y = 35

        # Instructions
        if self.editing:
            self.sys.draw_text("EDITING - Type your text", 5, y, scale=1, color=(255, 255, 0))
            y += 12
            self.sys.draw_text("[Enter] Done  [Backspace] Delete", 5, y, scale=1, color=(200, 200, 200))
            y += 20
        else:
            self.sys.draw_text("Press [Enter] to edit field", 5, y, scale=1, color=(200, 200, 200))
            y += 20

        # Draw fields
        for i, field_name in enumerate(self.fields):
            is_selected = (i == self.selected_index)
            is_editing = is_selected and self.editing

            # Get field value
            if i == 0:
                value = self.ssid if self.ssid else "<empty>"
                # Truncate if too long
                if len(value) > 30:
                    value = value[:27] + "..."
            elif i == 1:
                # Show password as asterisks
                if self.password:
                    value = "*" * min(len(self.password), 30)
                else:
                    value = "<empty>"
            elif i == 2:
                value = "Yes" if self.auto_connect else "No"

            # Draw field box
            box_height = 28
            if is_editing:
                # Editing - yellow box with cursor
                self.sys.draw_rect(3, y - 2, self.sys.width - 6, box_height, (255, 255, 0))
                name_color = (0, 0, 0)
                value_color = (0, 0, 128)
            elif is_selected:
                # Selected - cyan box
                self.sys.draw_rect(3, y - 2, self.sys.width - 6, box_height, (0, 255, 255))
                name_color = (0, 0, 0)
                value_color = (0, 0, 128)
            else:
                # Not selected - dark box
                self.sys.draw_rect(3, y - 2, self.sys.width - 6, box_height, (32, 32, 64))
                name_color = (200, 200, 200)
                value_color = (255, 255, 255)

            # Draw field name
            self.sys.draw_text(field_name + ":", 8, y + 2, scale=1, color=name_color)

            # Draw value with cursor if editing
            if is_editing:
                self.sys.draw_text(value + "_", 8, y + 14, scale=1, color=value_color)
            else:
                self.sys.draw_text(value, 8, y + 14, scale=1, color=value_color)

            y += box_height + 6

        # Status message
        if self.status_message:
            status_y = self.sys.height - 65
            self.sys.draw_rect(0, status_y - 2, self.sys.width, 16, (0, 100, 0))
            # Truncate long messages
            msg = self.status_message
            if len(msg) > 38:
                msg = msg[:35] + "..."
            self.sys.draw_text(msg, 5, status_y, scale=1, color=(255, 255, 255))

        # Controls at bottom
        controls_y = self.sys.height - 45
        if not self.editing:
            self.sys.draw_text("[Up/Down] Select", 5, controls_y, scale=1, color=(150, 150, 150))
            controls_y += 12
            self.sys.draw_text("[Enter] Edit  [C] Clear  [T] Test", 5, controls_y, scale=1, color=(150, 150, 150))
            controls_y += 12
            self.sys.draw_text("[F1] Save  [Esc] Quit", 5, controls_y, scale=1, color=(150, 150, 150))

        # Update display
        self.sys.update()
