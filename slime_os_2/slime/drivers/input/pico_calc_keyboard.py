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
        # ---------- JOYSTICK ----------
        0x01: Keycode.UP_ARROW,       # KEY_JOY_UP
        0x02: Keycode.DOWN_ARROW,     # KEY_JOY_DOWN
        0x03: Keycode.LEFT_ARROW,     # KEY_JOY_LEFT
        0x04: Keycode.RIGHT_ARROW,    # KEY_JOY_RIGHT
        0x05: Keycode.ENTER,          # KEY_JOY_CENTER

        0x06: Keycode.SHIFT,          # KEY_BTN_LEFT1
        0x07: Keycode.CONTROL,        # KEY_BTN_RIGHT1
        0x11: Keycode.ALT,            # KEY_BTN_LEFT2
        0x12: Keycode.GUI,            # KEY_BTN_RIGHT2

        # ---------- BASIC KEYS ----------
        0x08: Keycode.BACKSPACE,
        0x09: Keycode.TAB,
        0x0A: Keycode.RETURN,

        # ---------- MODIFIERS ----------
        0xA1: Keycode.ALT,            # KEY_MOD_ALT
        0xA2: Keycode.LEFT_SHIFT,     # KEY_MOD_SHL
        0xA3: Keycode.RIGHT_SHIFT,    # KEY_MOD_SHR
        0xA4: Keycode.GUI,            # KEY_MOD_SYM
        0xA5: Keycode.CONTROL,        # KEY_MOD_CTRL

        # ---------- NAVIGATION ----------
        0xB1: Keycode.ESCAPE,         # KEY_ESC
        0xB4: Keycode.LEFT_ARROW,     # KEY_LEFT
        0xB5: Keycode.UP_ARROW,       # KEY_UP
        0xB6: Keycode.DOWN_ARROW,     # KEY_DOWN
        0xB7: Keycode.RIGHT_ARROW,    # KEY_RIGHT

        0xD0: Keycode.PAUSE,          # KEY_BREAK
        0xD1: Keycode.INSERT,
        0xD2: Keycode.HOME,
        0xD4: Keycode.DELETE,
        0xD5: Keycode.END,
        0xD6: Keycode.PAGE_UP,
        0xD7: Keycode.PAGE_DOWN,

        0xC1: Keycode.CAPS_LOCK,

        # ---------- FUNCTION KEYS ----------
        0x81: Keycode.F1,
        0x82: Keycode.F2,
        0x83: Keycode.F3,
        0x84: Keycode.F4,
        0x85: Keycode.F5,
        0x86: Keycode.F6,
        0x87: Keycode.F7,
        0x88: Keycode.F8,
        0x89: Keycode.F9,
        0x90: Keycode.F10,

        0x91: Keycode.POWER,          # KEY_POWER


        # ---------- LOWERCASE LETTERS (ASCII 97-122) ----------
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

        # ---------- UPPERCASE LETTERS (ASCII 65-90) ----------
        65: Keycode.A_UPPER,
        66: Keycode.B_UPPER,
        67: Keycode.C_UPPER,
        68: Keycode.D_UPPER,
        69: Keycode.E_UPPER,
        70: Keycode.F_UPPER,
        71: Keycode.G_UPPER,
        72: Keycode.H_UPPER,
        73: Keycode.I_UPPER,
        74: Keycode.J_UPPER,
        75: Keycode.K_UPPER,
        76: Keycode.L_UPPER,
        77: Keycode.M_UPPER,
        78: Keycode.N_UPPER,
        79: Keycode.O_UPPER,
        80: Keycode.P_UPPER,
        81: Keycode.Q_UPPER,
        82: Keycode.R_UPPER,
        83: Keycode.S_UPPER,
        84: Keycode.T_UPPER,
        85: Keycode.U_UPPER,
        86: Keycode.V_UPPER,
        87: Keycode.W_UPPER,
        88: Keycode.X_UPPER,
        89: Keycode.Y_UPPER,
        90: Keycode.Z_UPPER,

        # ---------- SPECIAL CHARACTERS ----------
        8:  Keycode.BACKSPACE,
        9:  Keycode.TAB,
        10: Keycode.RETURN,
        32: Keycode.SPACE,
        44: Keycode.COMMA,
        46: Keycode.PERIOD,
        47: Keycode.FORWARD_SLASH,

        # ---------- ALTERNATE ARROWS ----------
        180: Keycode.LEFT_ARROW,
        181: Keycode.UP_ARROW,
        182: Keycode.DOWN_ARROW,
        183: Keycode.RIGHT_ARROW,

        # ---------- NUMBERS ----------
        0x30: Keycode.ZERO,
        0x31: Keycode.ONE,
        0x32: Keycode.TWO,
        0x33: Keycode.THREE,
        0x34: Keycode.FOUR,
        0x35: Keycode.FIVE,
        0x36: Keycode.SIX,
        0x37: Keycode.SEVEN,
        0x38: Keycode.EIGHT,
        0x39: Keycode.NINE,
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
            i2c: Initialized I2C bus instance (can be None for dummy mode)
        """
        self.i2c = i2c
        self.i2c_working = False  # Track if I2C is functional

        # Try to verify I2C is working
        if self.i2c is not None:
            try:
                devices = self.i2c.scan()
                if self.KEYBOARD_ADDR in devices:
                    self.i2c_working = True
                    print(f"[PicoCalcKeyboard] I2C bus verified, keyboard at address {self.KEYBOARD_ADDR}")
                else:
                    print(f"[PicoCalcKeyboard] WARNING: Keyboard not found at address {self.KEYBOARD_ADDR}")
            except Exception as e:
                print(f"[PicoCalcKeyboard] WARNING: I2C bus test failed: {e}")

        # Create inverse map: keycode -> raw_code
        self.inv_map = {v: k for k, v in self.KEY_MAP.items()}
        
        # Map standard keycodes to their upper/lower variants for caps-independent checking
        self._letter_variants = {
            Keycode.A: (Keycode.A, Keycode.A_UPPER),
            Keycode.B: (Keycode.B, Keycode.B_UPPER),
            Keycode.C: (Keycode.C, Keycode.C_UPPER),
            Keycode.D: (Keycode.D, Keycode.D_UPPER),
            Keycode.E: (Keycode.E, Keycode.E_UPPER),
            Keycode.F: (Keycode.F, Keycode.F_UPPER),
            Keycode.G: (Keycode.G, Keycode.G_UPPER),
            Keycode.H: (Keycode.H, Keycode.H_UPPER),
            Keycode.I: (Keycode.I, Keycode.I_UPPER),
            Keycode.J: (Keycode.J, Keycode.J_UPPER),
            Keycode.K: (Keycode.K, Keycode.K_UPPER),
            Keycode.L: (Keycode.L, Keycode.L_UPPER),
            Keycode.M: (Keycode.M, Keycode.M_UPPER),
            Keycode.N: (Keycode.N, Keycode.N_UPPER),
            Keycode.O: (Keycode.O, Keycode.O_UPPER),
            Keycode.P: (Keycode.P, Keycode.P_UPPER),
            Keycode.Q: (Keycode.Q, Keycode.Q_UPPER),
            Keycode.R: (Keycode.R, Keycode.R_UPPER),
            Keycode.S: (Keycode.S, Keycode.S_UPPER),
            Keycode.T: (Keycode.T, Keycode.T_UPPER),
            Keycode.U: (Keycode.U, Keycode.U_UPPER),
            Keycode.V: (Keycode.V, Keycode.V_UPPER),
            Keycode.W: (Keycode.W, Keycode.W_UPPER),
            Keycode.X: (Keycode.X, Keycode.X_UPPER),
            Keycode.Y: (Keycode.Y, Keycode.Y_UPPER),
            Keycode.Z: (Keycode.Z, Keycode.Z_UPPER),
        }

        # Track held keys
        self.held = {}
        for raw_code in self.KEY_MAP:
            self.held[raw_code] = False

        # Timeout tracking
        self.last_key_time = 0
        self.key_timeout_ms = 20  # Clear keys after 500ms of no activity

        self._last_print = None
        self._print_delay = 0.5
        self._error_count = 0
        self._max_errors_before_disable = 20  # Disable after too many errors
        self.shift_active = False
        self.caps_lock_active = False

    def _read_raw_data(self):
        """
        Read raw data from keyboard controller.

        Returns:
            Raw key code (positive for press, negative for release, 0 for no event)
        """
        # If I2C bus is None or we've had too many errors, don't try
        if self.i2c is None:
            return 0

        if self._error_count >= self._max_errors_before_disable:
            # Too many errors, stop trying to avoid spam
            return 0

        try:
            # Request data from keyboard
            self.i2c.writeto(self.KEYBOARD_ADDR, b'\x09')
            time.sleep_ms(4)  # Give controller time to respond

            # Read 2 bytes
            data = self.i2c.readfrom(self.KEYBOARD_ADDR, 2)
            value = (data[1] << 8) | data[0]  # Combine into 16-bit value

            # Reset error count on successful read
            if self._error_count > 0:
                self._error_count = 0
                print("[PicoCalcKeyboard] I2C recovered")

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

        except OSError as e:
            # I2C error - return no event
            self._error_count += 1
            now = time.time()
            if not self._last_print or now - self._last_print > self._print_delay:
                print(f"[PicoCalcKeyboard] I2C error ({self._error_count}/{self._max_errors_before_disable}): {e}")
                self._last_print = now

                if self._error_count >= self._max_errors_before_disable:
                    print(f"[PicoCalcKeyboard] Too many errors, keyboard disabled")
            return 0
        except Exception as e:
            # Unexpected error
            self._error_count += 1
            now = time.time()
            if not self._last_print or now - self._last_print > self._print_delay:
                print(f"[PicoCalcKeyboard] Unexpected error: {e}")
                self._last_print = now
            return 0

    def _update_key_state(self):
        """Update internal key state from hardware"""
        raw_code = self._read_raw_data()
        # Modifier tracking
        if raw_code in (self.inv_map.get(Keycode.LEFT_SHIFT),
                        self.inv_map.get(Keycode.RIGHT_SHIFT)):
            self.shift_active = (raw_code > 0)

        # Caps lock toggle (only on key press, not release)
        if raw_code > 0 and raw_code == self.inv_map.get(Keycode.CAPS_LOCK):
            self.caps_lock_active = not self.caps_lock_active

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

    def get_key(self, keycode, case_sensitive=False):
        """
        Check if a specific key is pressed.

        Args:
            keycode: Keycode constant (e.g., Keycode.A)
            case_sensitive: If True, only check the exact keycode. If False (default),
                          for letter keycodes, check both upper and lower variants.

        Returns:
            True if pressed, False otherwise
        """
        # Read from cached state (updated once per frame by system)
        # If case_sensitive is False and this is a letter keycode, check both variants
        if not case_sensitive and keycode in self._letter_variants:
            lower_keycode, upper_keycode = self._letter_variants[keycode]
            # Check both variants
            lower_raw = self.inv_map.get(lower_keycode, None)
            upper_raw = self.inv_map.get(upper_keycode, None)
            
            lower_pressed = lower_raw is not None and self.held.get(lower_raw, False)
            upper_pressed = upper_raw is not None and self.held.get(upper_raw, False)
            
            return lower_pressed or upper_pressed

        # Look up raw code for this keycode (case-sensitive or non-letter)
        raw_code = self.inv_map.get(keycode, None)
        if raw_code is None:
            return False  # Unknown keycode

        # Return held state
        return self.held.get(raw_code, False)

    def get_keys(self, keycodes, case_sensitive=False):
        """
        Check multiple keys at once.

        Args:
            keycodes: List of keycode constants
            case_sensitive: If True, only check exact keycodes. If False (default),
                          for letter keycodes, check both upper and lower variants.

        Returns:
            Dict mapping each keycode to True/False
        """
        # Read from cached state (updated once per frame by system)
        result = {}
        for keycode in keycodes:
            # Check each keycode from cached state
            if not case_sensitive and keycode in self._letter_variants:
                # Case-insensitive letter: check both upper and lower variants
                lower_keycode, upper_keycode = self._letter_variants[keycode]
                lower_raw = self.inv_map.get(lower_keycode, None)
                upper_raw = self.inv_map.get(upper_keycode, None)

                lower_pressed = lower_raw is not None and self.held.get(lower_raw, False)
                upper_pressed = upper_raw is not None and self.held.get(upper_raw, False)

                result[keycode] = lower_pressed or upper_pressed
            else:
                # Case-sensitive or non-letter: check exact keycode
                raw_code = self.inv_map.get(keycode, None)
                if raw_code is None:
                    result[keycode] = False  # Unknown keycode
                else:
                    result[keycode] = self.held.get(raw_code, False)

        return result
