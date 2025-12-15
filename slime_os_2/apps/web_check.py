"""
Web Test App

Simple app to test WiFi connectivity by fetching a webpage.
Shows the HTTP response and connection status.
"""

from slime.app import App
from lib.keycode import Keycode


class WebTestApp(App):
    """Web Test - simple HTTP request to test WiFi"""

    name = "Web Test"
    id = "web_test"

    TEST_URL = "http://httpbin.org/get"

    def __init__(self, system):
        super().__init__(system)
        self.status = "Not started"
        self.response_text = ""
        self.wifi_status = {}
        self.need_update = True

    def fetch_url(self, url):
        """
        Fetch a URL and return the response

        Returns:
            Tuple of (success: bool, response_text: str, error: str or None)
        """
        try:
            import urequests

            self.sys.log.info(f"Web: Fetching {url}...")
            self.status = f"Fetching {url}..."
            self.need_update = True

            response = urequests.get(url, timeout=10)

            # Get response text (limit to first 500 chars)
            text = response.text
            if len(text) > 500:
                text = text[:500] + "..."

            status_code = response.status_code
            response.close()

            self.sys.log.info(f"Web: Got response, status code: {status_code}")

            return (True, f"HTTP {status_code}\n\n{text}", None)

        except ImportError:
            error = "urequests module not available"
            self.sys.log.error(f"Web: {error}")
            return (False, "", error)
        except Exception as e:
            error = str(e)
            self.sys.log.error(f"Web: Request failed: {error}")
            return (False, "", error)

    def run(self):
        """Main app loop"""
        self.sys.log.info("Web Test app starting")

        # Check WiFi status
        self.wifi_status = self.sys.wifi_status()
        self.need_update = True

        while True:
            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.T,  # Test connection
                Keycode.C,  # Connect to WiFi
                Keycode.D,  # Disconnect
                Keycode.S,  # Status
                Keycode.Q   # Quit
            ])

            if keys[Keycode.T]:
                # Test web connection
                if not self.wifi_status.get('connected'):
                    self.status = "Not connected to WiFi!"
                    self.response_text = "Please connect to WiFi first (press C)"
                else:
                    success, response, error = self.fetch_url(self.TEST_URL)
                    if success:
                        self.status = "Success!"
                        self.response_text = response
                    else:
                        self.status = f"Failed: {error}"
                        self.response_text = ""
                self.need_update = True

            if keys[Keycode.C]:
                # Connect to WiFi
                self.status = "Connecting to WiFi..."
                self.need_update = True
                self._draw_ui()  # Show status immediately

                success, ip, error = self.sys.wifi_connect()
                if success:
                    self.status = f"Connected! IP: {ip}"
                    self.wifi_status = self.sys.wifi_status()
                else:
                    self.status = f"Connection failed: {error}"
                self.need_update = True

            if keys[Keycode.D]:
                # Disconnect from WiFi
                self.sys.wifi_disconnect()
                self.wifi_status = self.sys.wifi_status()
                self.status = "Disconnected"
                self.response_text = ""
                self.need_update = True

            if keys[Keycode.S]:
                # Refresh WiFi status
                self.wifi_status = self.sys.wifi_status()
                self.status = "Status refreshed"
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
        """Draw web test UI"""
        # Clear screen
        self.sys.clear((0, 16, 32))  # Dark teal background

        # Title
        self.sys.draw_text("Web Test", 5, 5, scale=2, color=(255, 255, 0))

        y = 30

        # WiFi Status
        self.sys.draw_text("WiFi Status:", 5, y, scale=1, color=(200, 200, 200))
        y += 15

        if self.wifi_status.get('connected'):
            status_color = (0, 255, 0)  # Green
            self.sys.draw_text(f"Connected to: {self.wifi_status.get('ssid', 'Unknown')}", 5, y, scale=1, color=status_color)
            y += 12
            self.sys.draw_text(f"IP: {self.wifi_status.get('ip')}", 5, y, scale=1, color=status_color)
            y += 12
        else:
            status_color = (255, 0, 0)  # Red
            self.sys.draw_text("Not connected", 5, y, scale=1, color=status_color)
            y += 12

        y += 5

        # Test Status
        self.sys.draw_text("Status:", 5, y, scale=1, color=(200, 200, 200))
        y += 15
        # Status message (may be multi-line if connection error)
        status_lines = self.status.split('\n')
        for line in status_lines[:2]:  # Max 2 lines
            self.sys.draw_text(line, 5, y, scale=1, color=(255, 255, 255))
            y += 12

        y += 8

        # Response (if any)
        if self.response_text:
            self.sys.draw_text("Response:", 5, y, scale=1, color=(200, 200, 200))
            y += 15

            # Split response into lines and show first few
            response_lines = self.response_text.split('\n')
            max_lines = (self.sys.height - y - 50) // 10  # Calculate how many lines fit
            for line in response_lines[:max_lines]:
                # Truncate long lines
                if len(line) > 38:
                    line = line[:35] + "..."
                self.sys.draw_text(line, 5, y, scale=1, color=(0, 255, 255))
                y += 10

        # Controls at bottom
        controls_y = self.sys.height - 38
        self.sys.draw_text("[T] Test  [C] Connect", 5, controls_y, scale=1, color=(150, 150, 150))
        controls_y += 12
        self.sys.draw_text("[D] Disconnect  [S] Status", 5, controls_y, scale=1, color=(150, 150, 150))
        controls_y += 12
        self.sys.draw_text("[Q] Quit", 5, controls_y, scale=1, color=(150, 150, 150))

        # Update display
        self.sys.update()
