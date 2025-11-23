#!/usr/bin/env python3
"""
Quick keyboard test for simulator

Press keys and see them detected. Press ESC to exit.
"""

import sys
import os

# Add compat to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'compat'))

import pygame
from slime.drivers.input.sim_keyboard import SimKeyboard
from lib.keycode import Keycode

def main():
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Keyboard Test")
    clock = pygame.time.Clock()

    keyboard = SimKeyboard()

    print("Keyboard test running!")
    print("Press keys to see them detected")
    print("Press ESC to exit")
    print()

    running = True
    while running:
        screen.fill((0, 0, 0))

        # Check some common keys
        keys = keyboard.get_keys([
            Keycode.A, Keycode.B, Keycode.C,
            Keycode.UP_ARROW, Keycode.DOWN_ARROW,
            Keycode.LEFT_ARROW, Keycode.RIGHT_ARROW,
            Keycode.ENTER, Keycode.SPACE,
            Keycode.ESCAPE, Keycode.Q
        ])

        pressed = [k for k, v in keys.items() if v]
        if pressed:
            print(f"Pressed: {[hex(k) for k in pressed]}")

        if keys[Keycode.ESCAPE]:
            print("ESC pressed - exiting")
            running = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    print("Test complete!")

if __name__ == '__main__':
    main()
