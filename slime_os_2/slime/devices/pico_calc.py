"""
Pico Calc device configuration

Hardware: Raspberry Pi Pico with 320x320 ST7789 display and I2C keyboard
"""

from .base import BaseDevice


class PicoCalcDevice(BaseDevice):
    """Pico Calc device profile"""

    # Metadata
    name = "Pico Calc"
    display_width = 320
    display_height = 320

    # Capabilities
    has_keyboard = True
    has_display = True
    has_sd_card = True

    # Hardware pin definitions
    # Keyboard (I2C)
    KEYBOARD_SCL = 7
    KEYBOARD_SDA = 6
    KEYBOARD_I2C_ID = 1

    # Display (SPI)
    DISPLAY_SCK = 10
    DISPLAY_MOSI = 11
    DISPLAY_CS = 13
    DISPLAY_DC = 14
    DISPLAY_RESET = 15
    DISPLAY_BACKLIGHT = 8

    # SD Card (SPI) - for future use
    SD_CARD_SCK = 18
    SD_CARD_MOSI = 19
    SD_CARD_MISO = 16
    SD_CARD_CS = 17

    def create_display(self):
        """Create Pico Calc display driver"""
        # Lazy import - only load driver when needed
        from slime.drivers.display.pico_calc_display import PicoCalcDisplay

        return PicoCalcDisplay(
            width=self.display_width,
            height=self.display_height,
            sck=self.DISPLAY_SCK,
            mosi=self.DISPLAY_MOSI,
            cs=self.DISPLAY_CS,
            dc=self.DISPLAY_DC,
            reset=self.DISPLAY_RESET,
            backlight=self.DISPLAY_BACKLIGHT
        )

    def create_input(self):
        """Create Pico Calc keyboard driver"""
        # Lazy import
        from slime.drivers.input.pico_calc_keyboard import PicoCalcKeyboard
        from machine import I2C, Pin
        import time

        print("[Keyboard] Initializing keyboard driver...")

        # Short delay before starting
        time.sleep_ms(100)

        # CRITICAL: Configure pins with pull-ups BEFORE creating I2C bus
        # The Pico Calc keyboard needs internal pull-ups enabled on I2C lines
        print("[Keyboard] Configuring I2C pins with pull-ups...")
        scl_pin = Pin(self.KEYBOARD_SCL, Pin.OUT, Pin.PULL_UP)
        sda_pin = Pin(self.KEYBOARD_SDA, Pin.OUT, Pin.PULL_UP)

        # Small delay for pull-ups to stabilize
        time.sleep_ms(50)

        # Create I2C bus
        print("[Keyboard] Creating I2C bus...")
        i2c = I2C(
            self.KEYBOARD_I2C_ID,
            scl=scl_pin,
            sda=sda_pin,
            freq=100000  # 100kHz standard speed
        )

        # Give I2C bus time to stabilize
        time.sleep_ms(100)

        # Scan for keyboard
        print("[Keyboard] Scanning for keyboard controller...")
        devices = i2c.scan()
        print(f"[Keyboard] Found I2C devices: {devices}")

        if PicoCalcKeyboard.KEYBOARD_ADDR in devices:
            print(f"[Keyboard] ✓ Keyboard found at address {PicoCalcKeyboard.KEYBOARD_ADDR}")
        else:
            print(f"[Keyboard] WARNING: Keyboard not found at address {PicoCalcKeyboard.KEYBOARD_ADDR}")
            print("[Keyboard] Keyboard will not respond to input")

        # Create keyboard driver and drain initial queue
        kbd = PicoCalcKeyboard(i2c)

        # Drain keyboard event queue (like reference implementation)
        print("[Keyboard] Draining initial event queue...")
        drain_count = 0
        for _ in range(100):  # Max 100 events to drain
            if kbd._read_raw_data() == 0:
                break
            drain_count += 1
            time.sleep_ms(10)

        if drain_count > 0:
            print(f"[Keyboard] Drained {drain_count} initial events")

        print("[Keyboard] Initialization complete")
        return kbd
