"""
Pico Calc Keyboard Driver

Hardware: I2C keyboard controller
Protocol: 16-bit value with action code (press/release) and key code
"""

from .abstract import AbstractInput
from lib.keycode import Keycode
import time


class PicoCalcKeyboard(AbstractInput):
    """
    Pico Calc I2C keyboard driver

    Communicates with keyboard controller over I2C to read key presses.
    Maintains key state with timeout for key release detection.
    """

    # Map raw key codes from hardware to USB HID keycodes
    KEY_MAP = {
        # Letters
        97: Keycode.A,
        98: Keycode.B,
        99: Keycode.C,
        100: Keycode.D,
        101: Keycode.E,
        102: Keycode.F,
        103: Keycode.G,
        104: Keycode.H,
        105: Keycode.I,
        106: Keycode.J,
        107: Keycode.K,
        108: Keycode.L,
        109: Keycode.M,
        110: Keycode.N,
        111: Keycode.O,
        112: Keycode.P,
        113: Keycode.Q,
        114: Keycode.R,
        115: Keycode.S,
        116: Keycode.T,
        117: Keycode.U,
        118: Keycode.V,
        119: Keycode.W,
        120: Keycode.X,
        121: Keycode.Y,
        122: Keycode.Z,

        # Special keys
        8: Keycode.BACKSPACE,
        9: Keycode.TAB,
        10: Keycode.RETURN,
        32: Keycode.SPACE,
        44: Keycode.COMMA,
        46: Keycode.PERIOD,
        47: Keycode.FORWARD_SLASH,

        # Arrow keys
        180: Keycode.LEFT_ARROW,
        181: Keycode.UP_ARROW,
        182: Keycode.DOWN_ARROW,
        183: Keycode.RIGHT_ARROW,
    }

    # I2C address of keyboard controller
    KEYBOARD_ADDR = 31

    # Action codes from keyboard protocol
    ACTION_PRESS = 1
    ACTION_RELEASE = 3

    def __init__(self, i2c):
        """
        Initialize keyboard driver.

        Args:
            i2c: Initialized I2C bus instance
        """
        self.i2c = i2c

        # Create inverse map: keycode -> raw_code
        self.inv_map = {v: k for k, v in self.KEY_MAP.items()}

        # Track held keys
        self.held = {}
        for raw_code in self.KEY_MAP:
            self.held[raw_code] = False

        # Timeout tracking
        self.last_key_time = 0
        self.key_timeout_ms = 500  # Clear keys after 500ms of no activity

    def _read_raw_data(self):
        """
        Read raw data from keyboard controller.

        Returns:
            Raw key code (positive for press, negative for release, 0 for no event)
        """
        try:
            # Request data from keyboard
            self.i2c.writeto(self.KEYBOARD_ADDR, b'\x09')
            time.sleep_ms(16)  # Give controller time to respond

            # Read 2 bytes
            data = self.i2c.readfrom(self.KEYBOARD_ADDR, 2)
            value = (data[1] << 8) | data[0]  # Combine into 16-bit value

            if value == 0:
                return 0  # No event

            # Parse protocol: low byte = action, high byte = key
            action_code = value & 0xFF
            key_code = value >> 8

            if action_code == self.ACTION_PRESS:
                return key_code  # Positive = press
            elif action_code == self.ACTION_RELEASE:
                return -key_code  # Negative = release

            return 0

        except Exception as e:
            # I2C error - return no event
            return 0

    def _update_key_state(self):
        """Update internal key state from hardware"""
        raw_code = self._read_raw_data()

        if raw_code == 0:
            # No event - check timeout
            if self.last_key_time != 0:
                if time.ticks_diff(time.ticks_ms(), self.last_key_time) > self.key_timeout_ms:
                    # Timeout - clear all held keys
                    for key in self.held:
                        self.held[key] = False
                    self.last_key_time = 0
        else:
            # Got event
            self.last_key_time = time.ticks_ms()

            if raw_code < 0:
                # Key release
                raw_code = -raw_code
                if raw_code in self.held:
                    self.held[raw_code] = False
            else:
                # Key press
                if raw_code in self.held:
                    self.held[raw_code] = True

    def get_key(self, keycode):
        """
        Check if a specific key is pressed.

        Args:
            keycode: Keycode constant (e.g., Keycode.A)

        Returns:
            True if pressed, False otherwise
        """
        # Update state from hardware
        self._update_key_state()

        # Look up raw code for this keycode
        raw_code = self.inv_map.get(keycode, None)
        if raw_code is None:
            return False  # Unknown keycode

        # Return held state
        return self.held.get(raw_code, False)

    def get_keys(self, keycodes):
        """
        Check multiple keys at once.

        Args:
            keycodes: List of keycode constants

        Returns:
            Dict mapping each keycode to True/False
        """
        # Update state once
        self._update_key_state()

        # Check each requested key
        result = {}
        for keycode in keycodes:
            raw_code = self.inv_map.get(keycode, None)
            if raw_code is None:
                result[keycode] = False
            else:
                result[keycode] = self.held.get(raw_code, False)

        return result
