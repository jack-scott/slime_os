"""
I2C Scanner App

Scans I2C buses for connected devices and displays them in a grid.
Useful for debugging and discovering I2C device addresses.
"""

from slime.app import App
from lib.keycode import Keycode


class I2CScannerApp(App):
    """I2C Scanner - scan I2C buses for devices"""

    name = "I2C Scanner"
    id = "i2c_scanner"

    def __init__(self, system):
        super().__init__(system)
        self.selected_bus = 1  # Default to I2C1 (keyboard bus on Pico Calc)
        self.found_devices = []
        self.scanning = False
        self.scan_error = None
        self.need_update = True

    def scan_i2c_bus(self, bus_id):
        """
        Scan I2C bus for devices.

        Args:
            bus_id: I2C bus number (0 or 1)

        Returns:
            List of device addresses found
        """
        self.scanning = True
        self.scan_error = None
        self.need_update = True

        try:
            from machine import I2C, Pin
            import time

            self.sys.log.info(f"I2C Scanner: Scanning bus {bus_id}...")

            # Configure I2C pins based on bus
            if bus_id == 0:
                # I2C0 - default Pico pins
                scl_pin = 1
                sda_pin = 0
            elif bus_id == 1:
                # I2C1 - keyboard bus on Pico Calc
                scl_pin = 7
                sda_pin = 6
            else:
                self.scan_error = f"Invalid bus ID: {bus_id}"
                return []

            # Create I2C bus with pull-ups
            scl = Pin(scl_pin, Pin.OUT, Pin.PULL_UP)
            sda = Pin(sda_pin, Pin.OUT, Pin.PULL_UP)
            time.sleep_ms(50)  # Let pull-ups stabilize

            i2c = I2C(bus_id, scl=scl, sda=sda, freq=100000)

            # Scan for devices
            devices = i2c.scan()
            self.sys.log.info(f"I2C Scanner: Found {len(devices)} devices on bus {bus_id}")

            return devices

        except ImportError:
            self.scan_error = "I2C not available (no machine module)"
            self.sys.log.error("I2C Scanner: machine module not available")
            return []
        except Exception as e:
            self.scan_error = f"Scan failed: {str(e)}"
            self.sys.log.error(f"I2C Scanner: Scan failed: {e}")
            return []
        finally:
            self.scanning = False

    def run(self):
        """Main app loop"""
        self.sys.log.info("I2C Scanner starting")

        # Initial scan
        self.found_devices = self.scan_i2c_bus(self.selected_bus)
        self.need_update = True

        while True:
            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.LEFT_ARROW,
                Keycode.RIGHT_ARROW,
                Keycode.R,
                Keycode.Q
            ])

            if keys[Keycode.LEFT_ARROW] and not self.scanning:
                # Switch to previous bus
                if self.selected_bus > 0:
                    self.selected_bus -= 1
                    self.found_devices = self.scan_i2c_bus(self.selected_bus)
                    self.need_update = True

            if keys[Keycode.RIGHT_ARROW] and not self.scanning:
                # Switch to next bus
                if self.selected_bus < 1:
                    self.selected_bus += 1
                    self.found_devices = self.scan_i2c_bus(self.selected_bus)
                    self.need_update = True

            if keys[Keycode.R] and not self.scanning:
                # Rescan current bus
                self.found_devices = self.scan_i2c_bus(self.selected_bus)
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
        """Draw I2C scanner UI"""
        # Clear screen
        self.sys.clear((0, 16, 32))  # Dark blue background

        # Title
        self.sys.draw_text("I2C Scanner", 5, 5, scale=2, color=(255, 255, 0))

        y = 30

        # Bus selection
        bus_text = f"Bus: I2C{self.selected_bus}"
        self.sys.draw_text(bus_text, 5, y, scale=1, color=(0, 255, 255))
        y += 15

        # Show scanning status or error
        if self.scanning:
            self.sys.draw_text("Scanning...", 5, y, scale=1, color=(255, 255, 0))
            y += 15
        elif self.scan_error:
            self.sys.draw_text("Error:", 5, y, scale=1, color=(255, 0, 0))
            y += 12
            self.sys.draw_text(self.scan_error, 5, y, scale=1, color=(255, 100, 100))
            y += 15
        else:
            # Show device count
            self.sys.draw_text(f"Found: {len(self.found_devices)} devices", 5, y, scale=1, color=(0, 255, 0))
            y += 15

        # Draw address grid
        if not self.scanning:
            y += 5
            self.sys.draw_text("Address Grid (0x00-0x7F):", 5, y, scale=1, color=(200, 200, 200))
            y += 15

            # Draw grid: 16 columns x 8 rows = 128 addresses
            cell_width = 18
            cell_height = 14
            start_x = 5
            start_y = y

            for row in range(8):
                for col in range(16):
                    addr = row * 16 + col
                    x = start_x + col * cell_width
                    y = start_y + row * cell_height

                    # Check if device found at this address
                    if addr in self.found_devices:
                        # Found - green background
                        self.sys.draw_rect(x, y, cell_width - 2, cell_height - 2, (0, 150, 0))
                        text_color = (255, 255, 255)
                    else:
                        # Not found - dark background
                        self.sys.draw_rect(x, y, cell_width - 2, cell_height - 2, (32, 32, 48))
                        text_color = (100, 100, 100)

                    # Draw address in hex (compact format)
                    addr_text = f"{addr:02X}"
                    self.sys.draw_text(addr_text, x + 2, y + 2, scale=1, color=text_color)

            # Draw found device list at bottom
            if self.found_devices:
                y = start_y + 8 * cell_height + 10
                self.sys.draw_text("Devices:", 5, y, scale=1, color=(255, 255, 0))
                y += 12

                # Show up to 5 devices with their addresses
                device_text = ", ".join([f"0x{addr:02X}" for addr in self.found_devices[:8]])
                if len(device_text) > 48:
                    device_text = device_text[:45] + "..."
                self.sys.draw_text(device_text, 5, y, scale=1, color=(0, 255, 0))

        # Controls at bottom
        controls_y = self.sys.height - 38
        self.sys.draw_text("[Left/Right] Change Bus", 5, controls_y, scale=1, color=(150, 150, 150))
        controls_y += 12
        self.sys.draw_text("[R] Rescan  [Q] Quit", 5, controls_y, scale=1, color=(150, 150, 150))

        # Update display
        self.sys.update()
