"""
Simulator Keyboard Driver

Pygame-based keyboard input for running Slime OS on desktop.
Maps PC keyboard to Slime OS keycodes.
"""

from .abstract import AbstractInput
from lib.keycode import Keycode

try:
    import pygame
except ImportError:
    print("ERROR: pygame not installed. Run: pip install pygame")
    raise


class SimKeyboard(AbstractInput):
    """
    Pygame-based virtual keyboard

    Captures PC keyboard input and maps to Slime OS keycodes.
    """

    # Map pygame keys to Slime OS keycodes
    KEY_MAP = {
        # Letters
        pygame.K_a: Keycode.A,
        pygame.K_b: Keycode.B,
        pygame.K_c: Keycode.C,
        pygame.K_d: Keycode.D,
        pygame.K_e: Keycode.E,
        pygame.K_f: Keycode.F,
        pygame.K_g: Keycode.G,
        pygame.K_h: Keycode.H,
        pygame.K_i: Keycode.I,
        pygame.K_j: Keycode.J,
        pygame.K_k: Keycode.K,
        pygame.K_l: Keycode.L,
        pygame.K_m: Keycode.M,
        pygame.K_n: Keycode.N,
        pygame.K_o: Keycode.O,
        pygame.K_p: Keycode.P,
        pygame.K_q: Keycode.Q,
        pygame.K_r: Keycode.R,
        pygame.K_s: Keycode.S,
        pygame.K_t: Keycode.T,
        pygame.K_u: Keycode.U,
        pygame.K_v: Keycode.V,
        pygame.K_w: Keycode.W,
        pygame.K_x: Keycode.X,
        pygame.K_y: Keycode.Y,
        pygame.K_z: Keycode.Z,

        # Numbers
        pygame.K_0: Keycode.ZERO,
        pygame.K_1: Keycode.ONE,
        pygame.K_2: Keycode.TWO,
        pygame.K_3: Keycode.THREE,
        pygame.K_4: Keycode.FOUR,
        pygame.K_5: Keycode.FIVE,
        pygame.K_6: Keycode.SIX,
        pygame.K_7: Keycode.SEVEN,
        pygame.K_8: Keycode.EIGHT,
        pygame.K_9: Keycode.NINE,

        # Special keys
        pygame.K_RETURN: Keycode.ENTER,
        pygame.K_ESCAPE: Keycode.ESCAPE,
        pygame.K_BACKSPACE: Keycode.BACKSPACE,
        pygame.K_TAB: Keycode.TAB,
        pygame.K_SPACE: Keycode.SPACE,
        pygame.K_COMMA: Keycode.COMMA,
        pygame.K_PERIOD: Keycode.PERIOD,
        pygame.K_SLASH: Keycode.FORWARD_SLASH,
        pygame.K_MINUS: Keycode.MINUS,
        pygame.K_EQUALS: Keycode.EQUALS,

        # Arrow keys
        pygame.K_UP: Keycode.UP_ARROW,
        pygame.K_DOWN: Keycode.DOWN_ARROW,
        pygame.K_LEFT: Keycode.LEFT_ARROW,
        pygame.K_RIGHT: Keycode.RIGHT_ARROW,

        # Function keys
        pygame.K_F1: Keycode.F1,
        pygame.K_F2: Keycode.F2,
        pygame.K_F3: Keycode.F3,
        pygame.K_F4: Keycode.F4,
        pygame.K_F5: Keycode.F5,
        pygame.K_F6: Keycode.F6,
        pygame.K_F7: Keycode.F7,
        pygame.K_F8: Keycode.F8,
        pygame.K_F9: Keycode.F9,
        pygame.K_F10: Keycode.F10,
        pygame.K_F11: Keycode.F11,
        pygame.K_F12: Keycode.F12,
    }

    def __init__(self):
        """Initialize keyboard driver"""
        # Create inverse map: keycode -> pygame key
        self.inv_map = {v: k for k, v in self.KEY_MAP.items()}

        # Track currently pressed keys
        self.pressed_keys = set()

        # Track keys that were pressed last frame (for edge detection)
        self.prev_pressed_keys = set()

        # Modifier states
        self.caps_lock_active = False

        print("[SimKeyboard] Initialized")

    def clear_state(self):
        """Clear all pressed keys (useful when launching new app)"""
        self.pressed_keys.clear()
        self.prev_pressed_keys.clear()

    def _update_key_state(self):
        """Update keyboard state from pygame"""
        # Process all pending events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                # Key pressed
                if event.key in self.KEY_MAP:
                    keycode = self.KEY_MAP[event.key]
                    self.pressed_keys.add(keycode)

                    # Toggle caps lock on press
                    if keycode == Keycode.CAPS_LOCK:
                        self.caps_lock_active = not self.caps_lock_active

            elif event.type == pygame.KEYUP:
                # Key released
                if event.key in self.KEY_MAP:
                    keycode = self.KEY_MAP[event.key]
                    self.pressed_keys.discard(keycode)

            elif event.type == pygame.QUIT:
                # Window closed
                raise SystemExit("Window closed")

    def get_key(self, keycode, case_sensitive=False):
        """
        Check if a specific key was just pressed (edge detection).

        Args:
            keycode: Keycode constant
            case_sensitive: Ignored for simulator (always case-sensitive)

        Returns:
            True if pressed this frame (not last frame), False otherwise
        """
        # Read from cached state (updated once per frame by system)
        # Check if key is newly pressed (pressed now, but not last frame)
        is_newly_pressed = keycode in self.pressed_keys and keycode not in self.prev_pressed_keys

        # Update previous state for next frame
        self.prev_pressed_keys = self.pressed_keys.copy()

        return is_newly_pressed

    def get_keys(self, keycodes, case_sensitive=False):
        """
        Check multiple keys at once (edge detection).

        Args:
            keycodes: List of keycode constants
            case_sensitive: Ignored for simulator (always case-sensitive)

        Returns:
            Dict mapping each keycode to True/False (True if newly pressed)
        """
        # Read from cached state (updated once per frame by system)
        # Check each key for new presses
        result = {}
        for keycode in keycodes:
            result[keycode] = keycode in self.pressed_keys and keycode not in self.prev_pressed_keys

        # Update previous state for next frame
        self.prev_pressed_keys = self.pressed_keys.copy()

        return result
