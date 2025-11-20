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

        # Create I2C bus for keyboard
        i2c = I2C(
            self.KEYBOARD_I2C_ID,
            scl=Pin(self.KEYBOARD_SCL),
            sda=Pin(self.KEYBOARD_SDA)
        )

        return PicoCalcKeyboard(i2c)
