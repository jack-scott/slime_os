"""
Pico Calc Battery Driver

Reads battery information from the keyboard controller (STM32),
which manages the AXP2101 power management chip.

The RP2040 communicates with the keyboard controller via I2C to get
battery data, rather than talking directly to the AXP2101.
"""

from .abstract import AbstractBattery
from machine import I2C, Pin
import time


# Keyboard controller I2C configuration
KEYBOARD_I2C_ADDRESS = 0x1F

# Register IDs (from keyboard controller firmware)
REG_ID_BAT = 0x0b  # Battery register


class PicoCalcBattery(AbstractBattery):
    """
    Pico Calc battery driver

    Communicates with the keyboard controller to read battery information.
    The keyboard controller (STM32) manages the AXP2101 and exposes
    battery data through register 0x0b.
    """

    def __init__(self, i2c_id, sda, scl, i2c_address, reg_percent, reg_vbat_h, reg_vbat_l, reg_charging_status):
        """
        Initialize the battery driver and I2C connection

        Args:
            i2c_id: I2C bus ID (should be 1)
            sda: SDA pin number (should be 6)
            scl: SCL pin number (should be 7)
            i2c_address: Keyboard controller I2C address (ignored, uses 0x1F)
            reg_percent: Battery register ID (ignored, uses 0x0b)
            reg_vbat_h: Not used (kept for compatibility)
            reg_vbat_l: Not used (kept for compatibility)
            reg_charging_status: Not used (kept for compatibility)
        """
        self.i2c_id = i2c_id
        self.sda = sda
        self.scl = scl

        self.i2c = None
        self._last_level = 0
        self._last_charging = False
        self._init_i2c()

    def _init_i2c(self):
        """Initialize I2C connection to keyboard controller"""
        try:
            # Use the same I2C bus as keyboard with pull-ups
            # IMPORTANT: Speed must be 10kHz to match keyboard controller
            scl_pin = Pin(self.scl, Pin.OUT, Pin.PULL_UP)
            sda_pin = Pin(self.sda, Pin.OUT, Pin.PULL_UP)

            self.i2c = I2C(self.i2c_id, scl=scl_pin, sda=sda_pin, freq=10000)

            devices = self.i2c.scan()
            print(f"[Battery] I2C devices found: {[hex(dev) for dev in devices]}")

            if KEYBOARD_I2C_ADDRESS in devices:
                print(f"[Battery] Keyboard controller found at address {hex(KEYBOARD_I2C_ADDRESS)}")
            else:
                print("[Battery] Warning: Keyboard controller not found on I2C bus")
                self.i2c = None

        except Exception as e:
            print(f"[Battery] I2C initialization error: {e}")
            self.i2c = None

    def _read_battery_data(self):
        """
        Read battery percentage and charging status from keyboard controller

        Protocol:
        1. Write register ID (0x0b) to keyboard controller
        2. Wait 16ms
        3. Read 2 bytes: [register_id, battery_data]
        4. battery_data format:
           - Bits 0-6: Battery percentage (0-100)
           - Bit 7: Charging status (1 = charging, 0 = not charging)
        """
        if self.i2c is None:
            return None, None

        try:
            # Write register ID to request battery data
            self.i2c.writeto(KEYBOARD_I2C_ADDRESS, bytes([REG_ID_BAT]))

            # Wait for keyboard controller to prepare response
            time.sleep_ms(16)

            # Read 2 bytes response
            response = self.i2c.readfrom(KEYBOARD_I2C_ADDRESS, 2)

            if len(response) == 2:
                register_id = response[0]
                battery_data = response[1]

                # Extract percentage (bits 0-6)
                percent = battery_data & 0x7F

                # Extract charging status (bit 7)
                is_charging = (battery_data & 0x80) != 0

                # Cache the values
                self._last_level = percent
                self._last_charging = is_charging

                return percent, is_charging
            else:
                print(f"[Battery] Unexpected response length: {len(response)}")
                return self._last_level, self._last_charging

        except Exception as e:
            print(f"[Battery] Error reading battery data: {e}")
            # Return cached values on error
            return self._last_level, self._last_charging

    def get_battery_level(self):
        """
        Get the current battery level.

        Returns:
            int: Battery level as percentage (0-100)
        """
        level, _ = self._read_battery_data()
        return level if level is not None else self._last_level

    def get_is_charging(self):
        """
        Check if the battery is currently charging.

        Returns:
            bool: True if charging, False otherwise
        """
        _, charging = self._read_battery_data()
        return charging if charging is not None else self._last_charging
