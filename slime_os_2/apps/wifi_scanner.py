"""
WiFi Scanner App

Scans for WiFi networks, allows connection with password entry, and manages WiFi settings.
Features:
- Scan and display nearby networks
- Select network and connect with password
- Save WiFi credentials
- Disconnect from network
- Show connection status
"""

from slime.app import App
from lib.keycode import Keycode


class WiFiScannerApp(App):
    """WiFi Scanner - scan, connect, and manage WiFi"""

    name = "WiFi Scanner"
    id = "wifi_scanner"

    # Keycode to character mapping (for password entry)
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

    # Uppercase keycodes set for fast lookup
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
        self.networks = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.need_update = True
        self.scanning = False
        self.scan_error = None
        self.lines_per_page = 11  # Reduced to fit controls

        # Password entry state
        self.entering_password = False
        self.password = ""
        self.selected_network = None

        # Status message
        self.status_message = ""
        self.status_timer = 0

        # App control
        self.should_quit = False

        # Pre-build list of all keycodes to check for password entry
        control_keys = [Keycode.BACKSPACE, Keycode.ENTER, Keycode.ESCAPE]
        modifier_keys = [Keycode.LEFT_SHIFT, Keycode.RIGHT_SHIFT]
        self._all_keys_to_check = control_keys + modifier_keys + list(self.KEYCODE_TO_CHAR.keys())

    def _get_saved_password(self, ssid):
        """Get saved password for an SSID, if any"""
        saved_passwords = self.sys.settings.get('wifi_saved_passwords', {})
        return saved_passwords.get(ssid, None)

    def _save_password(self, ssid, password):
        """Save password for an SSID"""
        saved_passwords = self.sys.settings.get('wifi_saved_passwords', {})
        saved_passwords[ssid] = password
        self.sys.settings.set('wifi_saved_passwords', saved_passwords)
        self.sys.settings.save()

    def scan_networks(self):
        """
        Scan for WiFi networks.

        Returns list of networks with their information.
        Each network is a dict with: ssid, rssi, channel, security
        """
        self.scanning = True
        self.scan_error = None
        self.need_update = True

        try:
            # Import network module
            import network

            # Create WLAN interface in station mode
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)

            # Scan for networks
            self.sys.log.info("WiFi: Starting scan...")
            networks_raw = wlan.scan()
            self.sys.log.info(f"WiFi: Found {len(networks_raw)} networks")

            # Parse scan results
            # Format: (ssid, bssid, channel, RSSI, security, hidden)
            networks = []
            for net in networks_raw:
                ssid = net[0].decode('utf-8') if net[0] else "<Hidden>"
                bssid = net[1]
                channel = net[2]
                rssi = net[3]
                security = net[4]
                hidden = net[5]

                # Convert security to readable format
                sec_type = self._security_type_name(security)

                networks.append({
                    'ssid': ssid,
                    'bssid': bssid,
                    'channel': channel,
                    'rssi': rssi,
                    'security': sec_type,
                    'security_code': security,
                    'hidden': hidden
                })

            # Sort by signal strength (strongest first)
            networks.sort(key=lambda n: n['rssi'], reverse=True)

            # Deactivate WLAN to save power (don't disconnect if connected)
            # wlan.active(False)

            return networks

        except ImportError:
            self.scan_error = "WiFi not available (no network module)"
            self.sys.log.error("WiFi: network module not available")
            return []
        except Exception as e:
            self.scan_error = f"Scan failed: {str(e)}"
            self.sys.log.error(f"WiFi: Scan failed: {e}")
            return []
        finally:
            self.scanning = False

    def _security_type_name(self, sec_type):
        """Convert security type code to readable name"""
        # Security types from MicroPython network module
        sec_types = {
            0: "Open",
            1: "WEP",
            2: "WPA-PSK",
            3: "WPA2-PSK",
            4: "WPA/WPA2-PSK",
            5: "WPA2-Enterprise"
        }
        return sec_types.get(sec_type, f"Unknown({sec_type})")

    def _signal_strength_bars(self, rssi):
        """
        Convert RSSI to signal strength bars.

        RSSI scale (dBm):
        -30 to -50: Excellent (4 bars)
        -50 to -60: Good (3 bars)
        -60 to -70: Fair (2 bars)
        -70 to -80: Weak (1 bar)
        < -80: Very weak (0 bars)
        """
        if rssi >= -50:
            return "####"
        elif rssi >= -60:
            return "### "
        elif rssi >= -70:
            return "##  "
        elif rssi >= -80:
            return "#   "
        else:
            return "    "

    def run(self):
        """Main app loop"""
        self.sys.log.info("WiFi Scanner starting")

        # Initial scan
        self.networks = self.scan_networks()
        self.need_update = True

        while True:
            # Check if we should quit
            if self.should_quit:
                return

            # Decrement status timer
            if self.status_timer > 0:
                self.status_timer -= 1
                if self.status_timer == 0:
                    self.status_message = ""
                    self.need_update = True

            # Handle input based on mode
            if self.entering_password:
                self._handle_password_entry()
            else:
                self._handle_network_selection()

            # Draw UI if needed
            if self.need_update:
                self._draw_ui()
                self.need_update = False

            yield

    def _handle_network_selection(self):
        """Handle input in network selection mode"""
        keys = self.sys.keys_pressed([
            Keycode.UP_ARROW,
            Keycode.DOWN_ARROW,
            Keycode.ENTER,
            Keycode.R,
            Keycode.D,
            Keycode.Q
        ])

        if keys[Keycode.UP_ARROW] and not self.scanning:
            # Scroll up
            if self.selected_index > 0:
                self.selected_index -= 1
                if self.selected_index < self.scroll_offset:
                    self.scroll_offset = self.selected_index
                self.need_update = True

        if keys[Keycode.DOWN_ARROW] and not self.scanning:
            # Scroll down
            if self.selected_index < len(self.networks) - 1:
                self.selected_index += 1
                if self.selected_index >= self.scroll_offset + self.lines_per_page:
                    self.scroll_offset = self.selected_index - self.lines_per_page + 1
                self.need_update = True

        if keys[Keycode.ENTER] and not self.scanning and self.networks:
            # Connect to selected network
            self.selected_network = self.networks[self.selected_index]

            # Check if network is open (no password needed)
            if self.selected_network['security_code'] == 0:
                # Open network - connect directly
                self.status_message = "Connecting..."
                self.need_update = True
                self._draw_ui()

                success, ip, error = self.sys.wifi_connect(
                    self.selected_network['ssid'],
                    "",  # No password
                    timeout=15
                )

                if success:
                    # Save to settings
                    self.sys.settings.set('wifi_ssid', self.selected_network['ssid'])
                    self.sys.settings.set('wifi_password', "")
                    self.sys.settings.save()
                    self.status_message = f"Connected! IP: {ip}"
                else:
                    self.status_message = f"Failed: {error}"

                self.status_timer = 120
                self.need_update = True
            else:
                # Secured network - check for saved password
                saved_password = self._get_saved_password(self.selected_network['ssid'])

                if saved_password:
                    # Try connecting with saved password
                    self.status_message = "Connecting (saved password)..."
                    self.need_update = True
                    self._draw_ui()

                    success, ip, error = self.sys.wifi_connect(
                        self.selected_network['ssid'],
                        saved_password,
                        timeout=15
                    )

                    if success:
                        # Save to current settings
                        self.sys.settings.set('wifi_ssid', self.selected_network['ssid'])
                        self.sys.settings.set('wifi_password', saved_password)
                        self.sys.settings.save()
                        self.status_message = f"Connected! IP: {ip}"
                        self.status_timer = 120
                        self.need_update = True
                    else:
                        # Saved password failed, prompt for new one
                        self.status_message = "Saved password failed, enter new password"
                        self.status_timer = 90
                        self.entering_password = True
                        self.password = ""
                        self.need_update = True
                else:
                    # No saved password - prompt for password entry
                    self.entering_password = True
                    self.password = ""
                    self.need_update = True

        if keys[Keycode.R] and not self.scanning:
            # Rescan
            self.selected_index = 0
            self.scroll_offset = 0
            self.networks = self.scan_networks()
            self.need_update = True

        if keys[Keycode.D] and not self.scanning:
            # Disconnect
            self.sys.wifi_disconnect()
            self.status_message = "Disconnected"
            self.status_timer = 90
            self.need_update = True

        if keys[Keycode.Q]:
            # Exit
            self.should_quit = True

    def _handle_password_entry(self):
        """Handle input in password entry mode"""
        # Check all keys for password input
        keys = self.sys.keys_pressed(self._all_keys_to_check, case_sensitive=True)

        # Check if shift is pressed
        shift_pressed = keys.get(Keycode.LEFT_SHIFT, False) or keys.get(Keycode.RIGHT_SHIFT, False)

        # Check control keys first
        if keys.get(Keycode.BACKSPACE, False):
            if len(self.password) > 0:
                self.password = self.password[:-1]
                self.need_update = True

        elif keys.get(Keycode.ENTER, False):
            # Connect with password
            self.entering_password = False
            self.status_message = "Connecting..."
            self.need_update = True
            self._draw_ui()

            success, ip, error = self.sys.wifi_connect(
                self.selected_network['ssid'],
                self.password,
                timeout=15
            )

            if success:
                # Save to current settings
                self.sys.settings.set('wifi_ssid', self.selected_network['ssid'])
                self.sys.settings.set('wifi_password', self.password)
                # Save to password database for future connections
                self._save_password(self.selected_network['ssid'], self.password)
                self.status_message = f"Connected! IP: {ip}"
            else:
                self.status_message = f"Failed: {error}"

            self.password = ""  # Clear password
            self.status_timer = 150
            self.need_update = True

        elif keys.get(Keycode.ESCAPE, False):
            # Cancel password entry
            self.entering_password = False
            self.password = ""
            self.need_update = True

        else:
            # Check character keys
            for keycode, char in self.KEYCODE_TO_CHAR.items():
                if keys.get(keycode, False):
                    # Apply shift transformations for non-letter characters
                    if shift_pressed and keycode not in self._UPPERCASE_KEYCODES:
                        shift_map = {
                            '0': ')', '1': '!', '2': '@', '3': '#', '4': '$',
                            '5': '%', '6': '^', '7': '&', '8': '*', '9': '(',
                            '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
                            ';': ':', "'": '"', ',': '<', '.': '>', '/': '?',
                            '`': '~'
                        }
                        char = shift_map.get(char, char)

                    self.password += char
                    self.need_update = True
                    break  # Only process one key per frame

    def _draw_ui(self):
        """Draw WiFi scanner UI"""
        # Clear screen
        self.sys.clear((0, 0, 32))  # Dark blue background

        # Title
        self.sys.draw_text("WiFi Scanner", 5, 5, scale=1, color=(255, 255, 0))

        y = 20

        # If entering password, show password entry screen
        if self.entering_password:
            self.sys.draw_text(f"Connect to: {self.selected_network['ssid']}", 5, y, scale=1, color=(200, 200, 200))
            y += 15

            self.sys.draw_text("Enter Password:", 5, y, scale=1, color=(255, 255, 0))
            y += 20

            # Show password as asterisks
            password_display = "*" * len(self.password) + "_"
            if len(password_display) > 30:
                password_display = password_display[:30]

            # Draw password box
            self.sys.draw_rect(3, y - 2, self.sys.width - 6, 18, (255, 255, 0))
            self.sys.draw_text(password_display, 8, y + 2, scale=1, color=(0, 0, 0))
            y += 25

            # Instructions
            self.sys.draw_text("[Enter] Connect  [Esc] Cancel", 5, y, scale=1, color=(150, 150, 150))
            y += 12
            self.sys.draw_text("[Backspace] Delete", 5, y, scale=1, color=(150, 150, 150))

        else:
            # Show scanning status or error
            if self.scanning:
                self.sys.draw_text("Scanning...", 5, y, scale=1, color=(255, 255, 0))
                y += 15
            elif self.scan_error:
                self.sys.draw_text("Error:", 5, y, scale=1, color=(255, 0, 0))
                y += 15
                self.sys.draw_text(self.scan_error, 5, y, scale=1, color=(255, 100, 100))
                y += 15
            else:
                # Show network count and legend
                self.sys.draw_text(f"{len(self.networks)} networks  L=locked *=saved", 5, y, scale=1, color=(200, 200, 200))
                y += 15

            # Draw network list
            if self.networks and not self.scanning:
                y += 5
                visible_networks = self.networks[self.scroll_offset:self.scroll_offset + self.lines_per_page]

                for i, network in enumerate(visible_networks):
                    network_index = self.scroll_offset + i
                    is_selected = (network_index == self.selected_index)

                    # Highlight selected network
                    if is_selected:
                        self.sys.draw_rect(2, y - 2, self.sys.width - 4, 14, (255, 255, 0))
                        text_color = (0, 0, 0)  # Black text on yellow
                    else:
                        text_color = (255, 255, 255)  # White text

                    # Draw signal strength bars
                    bars = self._signal_strength_bars(network['rssi'])
                    self.sys.draw_text(bars, 5, y, scale=1, color=text_color)

                    # Draw SSID (truncate if too long)
                    ssid = network['ssid']
                    if len(ssid) > 18:
                        ssid = ssid[:15] + "..."
                    self.sys.draw_text(ssid, 35, y, scale=1, color=text_color)

                    # Draw icons on the right
                    icons_x = self.sys.width - 15
                    # Draw lock icon if secured
                    if network['security_code'] != 0:
                        self.sys.draw_text("L", icons_x, y, scale=1, color=text_color)
                        icons_x -= 12  # Move left for next icon

                    # Draw star icon if we have saved password
                    if self._get_saved_password(network['ssid']):
                        self.sys.draw_text("*", icons_x, y, scale=1, color=text_color)

                    y += 14

                    # Stop if we run out of space
                    if y > self.sys.height - 60:
                        break

        # Status message
        if self.status_message:
            status_y = self.sys.height - 52
            self.sys.draw_rect(0, status_y - 2, self.sys.width, 14, (0, 100, 0))
            msg = self.status_message
            if len(msg) > 38:
                msg = msg[:35] + "..."
            self.sys.draw_text(msg, 5, status_y, scale=1, color=(255, 255, 255))

        # Controls at bottom
        if not self.entering_password:
            controls_y = self.sys.height - 38
            self.sys.draw_text("[Up/Down] Select  [Enter] Connect", 5, controls_y, scale=1, color=(150, 150, 150))
            controls_y += 12
            self.sys.draw_text("[R] Rescan  [D] Disconnect  [Q] Quit", 5, controls_y, scale=1, color=(150, 150, 150))

        # Update display
        self.sys.update()
