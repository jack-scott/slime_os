"""
Stub implementation of st7789 display module

Allows display driver code to import without errors in simulator.
The actual display is handled by SimDisplay using pygame.
"""


# Color order constants
RGB = 0
BGR = 1


def color565(r, g, b):
    """
    Convert RGB888 to RGB565.

    Args:
        r, g, b: Color components (0-255)

    Returns:
        16-bit color value
    """
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


class ST7789:
    """Stub ST7789 display class"""

    def __init__(self, spi, width, height, cs=None, dc=None, reset=None,
                 backlight=None, custom_init=None, rotation=0, color_order=RGB,
                 inversion=False, options=0, rotations=None, buffer_size=0):
        """Stub initialization"""
        self.width = width
        self.height = height
        # All other params ignored - display is handled by SimDisplay

    def init(self):
        """Initialize display (no-op)"""
        pass

    def on(self):
        """Turn display on (no-op)"""
        pass

    def off(self):
        """Turn display off (no-op)"""
        pass

    def fill(self, color):
        """Fill display with color (no-op)"""
        pass

    def fill_rect(self, x, y, w, h, color):
        """Draw filled rectangle (no-op)"""
        pass

    def pixel(self, x, y, color):
        """Draw pixel (no-op)"""
        pass

    def line(self, x1, y1, x2, y2, color):
        """Draw line (no-op)"""
        pass

    def draw(self, font, text, x, y, color, scale=1):
        """Draw text (no-op)"""
        pass

    def draw_len(self, font, text, scale=1):
        """Measure text (stub)"""
        return len(text) * 8 * scale  # Approximate

    def blit_buffer(self, buffer, x, y, w, h):
        """Blit buffer (no-op)"""
        pass
