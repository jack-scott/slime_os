"""
WiFi Scanner App

Scans for WiFi networks and displays information about them.
Shows: SSID, signal strength (RSSI), channel, and security type.
"""

from slime.app import App
from lib.keycode import Keycode


class WiFiScannerApp(App):
    """WiFi Scanner - scan and display nearby networks"""

    name = "WiFi Scanner"
    id = "wifi_scanner"

    def __init__(self, system):
        super().__init__(system)
        self.networks = []
        self.selected_index = 0
        self.scroll_offset = 0
        self.need_update = True
        self.scanning = False
        self.scan_error = None
        self.lines_per_page = 14  # Approx lines that fit on screen

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
                    'hidden': hidden
                })

            # Sort by signal strength (strongest first)
            networks.sort(key=lambda n: n['rssi'], reverse=True)

            # Deactivate WLAN to save power
            wlan.active(False)

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
            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.UP_ARROW,
                Keycode.DOWN_ARROW,
                Keycode.R,
                Keycode.Q
            ])

            if keys[Keycode.UP_ARROW] and not self.scanning:
                # Scroll up (show older entries)
                if self.selected_index > 0:
                    self.selected_index -= 1
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                    self.need_update = True

            if keys[Keycode.DOWN_ARROW] and not self.scanning:
                # Scroll down (show newer entries)
                if self.selected_index < len(self.networks) - 1:
                    self.selected_index += 1
                    if self.selected_index >= self.scroll_offset + self.lines_per_page:
                        self.scroll_offset = self.selected_index - self.lines_per_page + 1
                    self.need_update = True

            if keys[Keycode.R] and not self.scanning:
                # Rescan
                self.selected_index = 0
                self.scroll_offset = 0
                self.networks = self.scan_networks()
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
        """Draw WiFi scanner UI"""
        # Clear screen
        self.sys.clear((0, 0, 32))  # Dark blue background

        # Title
        self.sys.draw_text("WiFi Scanner", 5, 5, scale=1, color=(255, 255, 0))

        y = 20

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
            # Show network count
            self.sys.draw_text(f"{len(self.networks)} networks found", 5, y, scale=1, color=(200, 200, 200))
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
                if len(ssid) > 20:
                    ssid = ssid[:17] + "..."
                self.sys.draw_text(ssid, 35, y, scale=1, color=text_color)

                y += 14

                # Stop if we run out of space
                if y > self.sys.height - 70:
                    break

        # Draw selected network details at bottom (left side)
        if self.networks and not self.scanning and self.selected_index < len(self.networks):
            network = self.networks[self.selected_index]

            # Draw separator line
            details_y = self.sys.height - 38
            self.sys.draw_rect(0, details_y - 2, self.sys.width, 1, (100, 100, 100))

            # Network details (left side)
            self.sys.draw_text("Details:", 5, details_y, scale=1, color=(255, 255, 0))
            details_y += 12
            self.sys.draw_text(f"RSSI: {network['rssi']} dBm", 5, details_y, scale=1, color=(200, 200, 200))
            details_y += 12
            self.sys.draw_text(f"Ch: {network['channel']}  {network['security']}", 5, details_y, scale=1, color=(200, 200, 200))

        # Controls at bottom right (separate from details)
        controls_y = self.sys.height - 38
        controls_x = self.sys.width // 2 + 10  # Right half of screen
        self.sys.draw_text("[Up/Down] Select", controls_x, controls_y, scale=1, color=(150, 150, 150))
        controls_y += 12
        self.sys.draw_text("[R] Rescan", controls_x, controls_y, scale=1, color=(150, 150, 150))
        controls_y += 12
        self.sys.draw_text("[Q] Quit", controls_x, controls_y, scale=1, color=(150, 150, 150))

        # Update display
        self.sys.update()
