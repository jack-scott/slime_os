# SPDX-FileCopyrightText: 2017 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_hid.keycode.Keycode`
====================================================

* Author(s): Scott Shawcroft, Dan Halbert
"""


class Keycode:
    """USB HID Keycode constants.

    This list is modeled after the names for USB keycodes defined in
    https://usb.org/sites/default/files/hut1_21_0.pdf#page=83.
    This list does not include every single code, but does include all the keys on
    a regular PC or Mac keyboard.

    Remember that keycodes are the names for key *positions* on a US keyboard, and may
    not correspond to the character that you mean to send if you want to emulate non-US keyboard.
    For instance, on a French keyboard (AZERTY instead of QWERTY),
    the keycode for 'q' is used to indicate an 'a'. Likewise, 'y' represents 'z' on
    a German keyboard. This is historical: the idea was that the keycaps could be changed
    without changing the keycodes sent, so that different firmware was not needed for
    different variations of a keyboard.
    """

    # pylint: disable-msg=invalid-name
    A = 0x04
    """``a`` and ``A``"""
    B = 0x05
    """``b`` and ``B``"""
    C = 0x06
    """``c`` and ``C``"""
    D = 0x07
    """``d`` and ``D``"""
    E = 0x08
    """``e`` and ``E``"""
    F = 0x09
    """``f`` and ``F``"""
    G = 0x0A
    """``g`` and ``G``"""
    H = 0x0B
    """``h`` and ``H``"""
    I = 0x0C
    """``i`` and ``I``"""
    J = 0x0D
    """``j`` and ``J``"""
    K = 0x0E
    """``k`` and ``K``"""
    L = 0x0F
    """``l`` and ``L``"""
    M = 0x10
    """``m`` and ``M``"""
    N = 0x11
    """``n`` and ``N``"""
    O = 0x12
    """``o`` and ``O``"""
    P = 0x13
    """``p`` and ``P``"""
    Q = 0x14
    """``q`` and ``Q``"""
    R = 0x15
    """``r`` and ``R``"""
    S = 0x16
    """``s`` and ``S``"""
    T = 0x17
    """``t`` and ``T``"""
    U = 0x18
    """``u`` and ``U``"""
    V = 0x19
    """``v`` and ``V``"""
    W = 0x1A
    """``w`` and ``W``"""
    X = 0x1B
    """``x`` and ``X``"""
    Y = 0x1C
    """``y`` and ``Y``"""
    Z = 0x1D
    """``z`` and ``Z``"""

    ONE = 0x1E
    """``1`` and ``!``"""
    TWO = 0x1F
    """``2`` and ``@``"""
    THREE = 0x20
    """``3`` and ``#``"""
    FOUR = 0x21
    """``4`` and ``$``"""
    FIVE = 0x22
    """``5`` and ``%``"""
    SIX = 0x23
    """``6`` and ``^``"""
    SEVEN = 0x24
    """``7`` and ``&``"""
    EIGHT = 0x25
    """``8`` and ``*``"""
    NINE = 0x26
    """``9`` and ``(``"""
    ZERO = 0x27
    """``0`` and ``)``"""
    ENTER = 0x28
    """Enter (Return)"""
    RETURN = ENTER
    """Alias for ``ENTER``"""
    ESCAPE = 0x29
    """Escape"""
    BACKSPACE = 0x2A
    """Delete backward (Backspace)"""
    TAB = 0x2B
    """Tab and Backtab"""
    SPACEBAR = 0x2C
    """Spacebar"""
    SPACE = SPACEBAR
    """Alias for SPACEBAR"""
    MINUS = 0x2D
    """``-` and ``_``"""
    EQUALS = 0x2E
    """``=` and ``+``"""
    LEFT_BRACKET = 0x2F
    """``[`` and ``{``"""
    RIGHT_BRACKET = 0x30
    """``]`` and ``}``"""
    BACKSLASH = 0x31
    r"""``\`` and ``|``"""
    POUND = 0x32
    """``#`` and ``~`` (Non-US keyboard)"""
    SEMICOLON = 0x33
    """``;`` and ``:``"""
    QUOTE = 0x34
    """``'`` and ``"``"""
    GRAVE_ACCENT = 0x35
    r""":literal:`\`` and ``~``"""
    COMMA = 0x36
    """``,`` and ``<``"""
    PERIOD = 0x37
    """``.`` and ``>``"""
    FORWARD_SLASH = 0x38
    """``/`` and ``?``"""

    CAPS_LOCK = 0x39
    """Caps Lock"""

    F1 = 0x3A
    """Function key F1"""
    F2 = 0x3B
    """Function key F2"""
    F3 = 0x3C
    """Function key F3"""
    F4 = 0x3D
    """Function key F4"""
    F5 = 0x3E
    """Function key F5"""
    F6 = 0x3F
    """Function key F6"""
    F7 = 0x40
    """Function key F7"""
    F8 = 0x41
    """Function key F8"""
    F9 = 0x42
    """Function key F9"""
    F10 = 0x43
    """Function key F10"""
    F11 = 0x44
    """Function key F11"""
    F12 = 0x45
    """Function key F12"""

    PRINT_SCREEN = 0x46
    """Print Screen (SysRq)"""
    SCROLL_LOCK = 0x47
    """Scroll Lock"""
    PAUSE = 0x48
    """Pause (Break)"""

    INSERT = 0x49
    """Insert"""
    HOME = 0x4A
    """Home (often moves to beginning of line)"""
    PAGE_UP = 0x4B
    """Go back one page"""
    DELETE = 0x4C
    """Delete forward"""
    END = 0x4D
    """End (often moves to end of line)"""
    PAGE_DOWN = 0x4E
    """Go forward one page"""

    RIGHT_ARROW = 0x4F
    """Move the cursor right"""
    LEFT_ARROW = 0x50
    """Move the cursor left"""
    DOWN_ARROW = 0x51
    """Move the cursor down"""
    UP_ARROW = 0x52
    """Move the cursor up"""

    KEYPAD_NUMLOCK = 0x53
    """Num Lock (Clear on Mac)"""
    KEYPAD_FORWARD_SLASH = 0x54
    """Keypad ``/``"""
    KEYPAD_ASTERISK = 0x55
    """Keypad ``*``"""
    KEYPAD_MINUS = 0x56
    """Keyapd ``-``"""
    KEYPAD_PLUS = 0x57
    """Keypad ``+``"""
    KEYPAD_ENTER = 0x58
    """Keypad Enter"""
    KEYPAD_ONE = 0x59
    """Keypad ``1`` and End"""
    KEYPAD_TWO = 0x5A
    """Keypad ``2`` and Down Arrow"""
    KEYPAD_THREE = 0x5B
    """Keypad ``3`` and PgDn"""
    KEYPAD_FOUR = 0x5C
    """Keypad ``4`` and Left Arrow"""
    KEYPAD_FIVE = 0x5D
    """Keypad ``5``"""
    KEYPAD_SIX = 0x5E
    """Keypad ``6`` and Right Arrow"""
    KEYPAD_SEVEN = 0x5F
    """Keypad ``7`` and Home"""
    KEYPAD_EIGHT = 0x60
    """Keypad ``8`` and Up Arrow"""
    KEYPAD_NINE = 0x61
    """Keypad ``9`` and PgUp"""
    KEYPAD_ZERO = 0x62
    """Keypad ``0`` and Ins"""
    KEYPAD_PERIOD = 0x63
    """Keypad ``.`` and Del"""
    KEYPAD_BACKSLASH = 0x64
    """Keypad ``\\`` and ``|`` (Non-US)"""

    APPLICATION = 0x65
    """Application: also known as the Menu key (Windows)"""
    POWER = 0x66
    """Power (Mac)"""
    KEYPAD_EQUALS = 0x67
    """Keypad ``=`` (Mac)"""
    F13 = 0x68
    """Function key F13 (Mac)"""
    F14 = 0x69
    """Function key F14 (Mac)"""
    F15 = 0x6A
    """Function key F15 (Mac)"""
    F16 = 0x6B
    """Function key F16 (Mac)"""
    F17 = 0x6C
    """Function key F17 (Mac)"""
    F18 = 0x6D
    """Function key F18 (Mac)"""
    F19 = 0x6E
    """Function key F19 (Mac)"""

    F20 = 0x6F
    """Function key F20"""
    F21 = 0x70
    """Function key F21"""
    F22 = 0x71
    """Function key F22"""
    F23 = 0x72
    """Function key F23"""
    F24 = 0x73
    """Function key F24"""

    LEFT_CONTROL = 0xE0
    """Control modifier left of the spacebar"""
    CONTROL = LEFT_CONTROL
    """Alias for LEFT_CONTROL"""
    LEFT_SHIFT = 0xE1
    """Shift modifier left of the spacebar"""
    SHIFT = LEFT_SHIFT
    """Alias for LEFT_SHIFT"""
    LEFT_ALT = 0xE2
    """Alt modifier left of the spacebar"""
    ALT = LEFT_ALT
    """Alias for LEFT_ALT; Alt is also known as Option (Mac)"""
    OPTION = ALT
    """Labeled as Option on some Mac keyboards"""
    LEFT_GUI = 0xE3
    """GUI modifier left of the spacebar"""
    GUI = LEFT_GUI
    """Alias for LEFT_GUI; GUI is also known as the Windows key, Command (Mac), or Meta"""
    WINDOWS = GUI
    """Labeled with a Windows logo on Windows keyboards"""
    COMMAND = GUI
    """Labeled as Command on Mac keyboards, with a clover glyph"""
    RIGHT_CONTROL = 0xE4
    """Control modifier right of the spacebar"""
    RIGHT_SHIFT = 0xE5
    """Shift modifier right of the spacebar"""
    RIGHT_ALT = 0xE6
    """Alt modifier right of the spacebar"""
    RIGHT_GUI = 0xE7
    """GUI modifier right of the spacebar"""

    # pylint: enable-msg=invalid-name
    @classmethod
    def modifier_bit(cls, keycode: int) -> int:
        """Return the modifer bit to be set in an HID keycode report if this is a
        modifier key; otherwise return 0."""
        return (
            1 << (keycode - 0xE0) if cls.LEFT_CONTROL <= keycode <= cls.RIGHT_GUI else 0
        )


keycode_as_str = {4: 'Keycode.A', 5: 'Keycode.B', 6: 'Keycode.C', 7: 'Keycode.D', 8: 'Keycode.E', 9: 'Keycode.F', 10: 'Keycode.G', 11: 'Keycode.H', 12: 'Keycode.I', 13: 'Keycode.J', 14: 'Keycode.K', 15: 'Keycode.L', 16: 'Keycode.M', 17: 'Keycode.N', 18: 'Keycode.O', 19: 'Keycode.P', 20: 'Keycode.Q', 21: 'Keycode.R', 22: 'Keycode.S', 23: 'Keycode.T', 24: 'Keycode.U', 25: 'Keycode.V', 26: 'Keycode.W', 27: 'Keycode.X', 28: 'Keycode.Y', 29: 'Keycode.Z', 30: 'Keycode.ONE', 31: 'Keycode.TWO', 32: 'Keycode.THREE', 33: 'Keycode.FOUR', 34: 'Keycode.FIVE', 35: 'Keycode.SIX', 36: 'Keycode.SEVEN', 37: 'Keycode.EIGHT', 38: 'Keycode.NINE', 39: 'Keycode.ZERO', 40: 'Keycode.RETURN', 41: 'Keycode.ESCAPE', 42: 'Keycode.BACKSPACE', 43: 'Keycode.TAB', 44: 'Keycode.SPACE', 45: 'Keycode.MINUS', 46: 'Keycode.EQUALS', 47: 'Keycode.LEFT_BRACKET', 48: 'Keycode.RIGHT_BRACKET', 49: 'Keycode.BACKSLASH', 50: 'Keycode.POUND', 51: 'Keycode.SEMICOLON', 52: 'Keycode.QUOTE', 53: 'Keycode.GRAVE_ACCENT', 54: 'Keycode.COMMA', 55: 'Keycode.PERIOD', 56: 'Keycode.FORWARD_SLASH', 57: 'Keycode.CAPS_LOCK', 58: 'Keycode.F1', 59: 'Keycode.F2', 60: 'Keycode.F3', 61: 'Keycode.F4', 62: 'Keycode.F5', 63: 'Keycode.F6', 64: 'Keycode.F7', 65: 'Keycode.F8', 66: 'Keycode.F9', 67: 'Keycode.F10', 68: 'Keycode.F11', 69: 'Keycode.F12', 70: 'Keycode.PRINT_SCREEN', 71: 'Keycode.SCROLL_LOCK', 72: 'Keycode.PAUSE', 73: 'Keycode.INSERT', 74: 'Keycode.HOME', 75: 'Keycode.PAGE_UP', 76: 'Keycode.DELETE', 77: 'Keycode.END', 78: 'Keycode.PAGE_DOWN', 79: 'Keycode.RIGHT_ARROW', 80: 'Keycode.LEFT_ARROW', 81: 'Keycode.DOWN_ARROW', 82: 'Keycode.UP_ARROW', 83: 'Keycode.KEYPAD_NUMLOCK', 84: 'Keycode.KEYPAD_FORWARD_SLASH', 85: 'Keycode.KEYPAD_ASTERISK', 86: 'Keycode.KEYPAD_MINUS', 87: 'Keycode.KEYPAD_PLUS', 88: 'Keycode.KEYPAD_ENTER', 89: 'Keycode.KEYPAD_ONE', 90: 'Keycode.KEYPAD_TWO', 91: 'Keycode.KEYPAD_THREE', 92: 'Keycode.KEYPAD_FOUR', 93: 'Keycode.KEYPAD_FIVE', 94: 'Keycode.KEYPAD_SIX', 95: 'Keycode.KEYPAD_SEVEN', 96: 'Keycode.KEYPAD_EIGHT', 97: 'Keycode.KEYPAD_NINE', 98: 'Keycode.KEYPAD_ZERO', 99: 'Keycode.KEYPAD_PERIOD', 100: 'Keycode.KEYPAD_BACKSLASH', 101: 'Keycode.APPLICATION', 102: 'Keycode.POWER', 103: 'Keycode.KEYPAD_EQUALS', 104: 'Keycode.F13', 105: 'Keycode.F14', 106: 'Keycode.F15', 107: 'Keycode.F16', 108: 'Keycode.F17', 109: 'Keycode.F18', 110: 'Keycode.F19', 111: 'Keycode.F20', 112: 'Keycode.F21', 113: 'Keycode.F22', 114: 'Keycode.F23', 115: 'Keycode.F24', 224: 'Keycode.CONTROL', 225: 'Keycode.SHIFT', 226: 'Keycode.OPTION', 227: 'Keycode.COMMAND', 228: 'Keycode.RIGHT_CONTROL', 229: 'Keycode.RIGHT_SHIFT', 230: 'Keycode.RIGHT_ALT', 231: 'Keycode.RIGHT_GUI'}