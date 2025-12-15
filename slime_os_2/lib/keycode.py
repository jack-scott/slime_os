# SPDX-FileCopyrightText: 2017 Scott Shawcroft for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
USB HID Keycode constants

This list is modeled after the names for USB keycodes defined in
https://usb.org/sites/default/files/hut1_21_0.pdf#page=83
"""


class Keycode:
    """USB HID Keycode constants"""

    # Letters
    A = 0x04
    B = 0x05
    C = 0x06
    D = 0x07
    E = 0x08
    F = 0x09
    G = 0x0A
    H = 0x0B
    I = 0x0C
    J = 0x0D
    K = 0x0E
    L = 0x0F
    M = 0x10
    N = 0x11
    O = 0x12
    P = 0x13
    Q = 0x14
    R = 0x15
    S = 0x16
    T = 0x17
    U = 0x18
    V = 0x19
    W = 0x1A
    X = 0x1B
    Y = 0x1C
    Z = 0x1D

    # Uppercase letter variants (for caps-aware keyboards)
    A_UPPER = 0x100
    B_UPPER = 0x101
    C_UPPER = 0x102
    D_UPPER = 0x103
    E_UPPER = 0x104
    F_UPPER = 0x105
    G_UPPER = 0x106
    H_UPPER = 0x107
    I_UPPER = 0x108
    J_UPPER = 0x109
    K_UPPER = 0x10A
    L_UPPER = 0x10B
    M_UPPER = 0x10C
    N_UPPER = 0x10D
    O_UPPER = 0x10E
    P_UPPER = 0x10F
    Q_UPPER = 0x110
    R_UPPER = 0x111
    S_UPPER = 0x112
    T_UPPER = 0x113
    U_UPPER = 0x114
    V_UPPER = 0x115
    W_UPPER = 0x116
    X_UPPER = 0x117
    Y_UPPER = 0x118
    Z_UPPER = 0x119

    # Lowercase letter variants (aliases for standard keycodes)
    A_LOWER = A
    B_LOWER = B
    C_LOWER = C
    D_LOWER = D
    E_LOWER = E
    F_LOWER = F
    G_LOWER = G
    H_LOWER = H
    I_LOWER = I
    J_LOWER = J
    K_LOWER = K
    L_LOWER = L
    M_LOWER = M
    N_LOWER = N
    O_LOWER = O
    P_LOWER = P
    Q_LOWER = Q
    R_LOWER = R
    S_LOWER = S
    T_LOWER = T
    U_LOWER = U
    V_LOWER = V
    W_LOWER = W
    X_LOWER = X
    Y_LOWER = Y
    Z_LOWER = Z

    # Numbers
    ONE = 0x1E
    TWO = 0x1F
    THREE = 0x20
    FOUR = 0x21
    FIVE = 0x22
    SIX = 0x23
    SEVEN = 0x24
    EIGHT = 0x25
    NINE = 0x26
    ZERO = 0x27

    # Special keys
    ENTER = 0x28
    RETURN = ENTER
    ESCAPE = 0x29
    BACKSPACE = 0x2A
    TAB = 0x2B
    SPACEBAR = 0x2C
    SPACE = SPACEBAR
    MINUS = 0x2D
    EQUALS = 0x2E
    LEFT_BRACKET = 0x2F
    RIGHT_BRACKET = 0x30
    BACKSLASH = 0x31
    POUND = 0x32
    SEMICOLON = 0x33
    QUOTE = 0x34
    GRAVE_ACCENT = 0x35
    COMMA = 0x36
    PERIOD = 0x37
    FORWARD_SLASH = 0x38

    CAPS_LOCK = 0x39

    # Function keys
    F1 = 0x3A
    F2 = 0x3B
    F3 = 0x3C
    F4 = 0x3D
    F5 = 0x3E
    F6 = 0x3F
    F7 = 0x40
    F8 = 0x41
    F9 = 0x42
    F10 = 0x43
    F11 = 0x44
    F12 = 0x45

    # Navigation keys
    PRINT_SCREEN = 0x46
    SCROLL_LOCK = 0x47
    PAUSE = 0x48
    INSERT = 0x49
    HOME = 0x4A
    PAGE_UP = 0x4B
    DELETE = 0x4C
    END = 0x4D
    PAGE_DOWN = 0x4E

    # Arrow keys
    RIGHT_ARROW = 0x4F
    LEFT_ARROW = 0x50
    DOWN_ARROW = 0x51
    UP_ARROW = 0x52

    # Modifier keys
    LEFT_CONTROL = 0xE0
    CONTROL = LEFT_CONTROL
    LEFT_SHIFT = 0xE1
    SHIFT = LEFT_SHIFT
    LEFT_ALT = 0xE2
    ALT = LEFT_ALT
    OPTION = ALT
    LEFT_GUI = 0xE3
    GUI = LEFT_GUI
    WINDOWS = GUI
    COMMAND = GUI
    RIGHT_CONTROL = 0xE4
    RIGHT_SHIFT = 0xE5
    RIGHT_ALT = 0xE6
    RIGHT_GUI = 0xE7
    POWER = 0x81  # not standard in HID keyboard page, but usable for your own mapping
