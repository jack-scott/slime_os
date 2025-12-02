"""
Simulator Display Driver

Pygame-based virtual display for running Slime OS on desktop.
Uses the same MicroFont bitmap font as hardware for pixel-perfect simulation.
"""

from .abstract import AbstractDisplay
from .microfont import MicroFont
import os

try:
    import pygame
except ImportError:
    print("ERROR: pygame not installed. Run: pip install pygame")
    raise


class SimDisplay(AbstractDisplay):
    """
    Pygame-based virtual display

    Creates a window that simulates the hardware display.
    Supports all AbstractDisplay methods.
    """

    def __init__(self, width, height, scale=2, title="Slime OS Simulator"):
        """
        Initialize simulator display.

        Args:
            width, height: Display dimensions (e.g., 320x320)
            scale: Window scale factor (1=native, 2=double size, etc.)
            title: Window title
        """
        super().__init__(width, height)

        self.scale = scale
        self.title = title

        # Initialize pygame
        pygame.init()

        # Create window (scaled for visibility)
        window_size = (width * scale, height * scale)
        self.window = pygame.display.set_mode(window_size)
        pygame.display.set_caption(title)

        # Create drawing surface at native resolution
        self.surface = pygame.Surface((width, height))
        self.surface.fill((0, 0, 0))  # Black

        # Current pen color (RGB)
        self.pen_color = (255, 255, 255)  # White

        # Load MicroFonts - same bitmap fonts as hardware at different sizes
        try:
            font_dir = os.path.dirname(__file__)
            font_1_path = os.path.join(font_dir, "victor:B:12.mfnt")
            font_2_path = os.path.join(font_dir, "victor:B:18.mfnt")
            font_3_path = os.path.join(font_dir, "victor:B:32.mfnt")

            # Load all available fonts (cache chars in simulator for speed)
            self.fonts = [
                MicroFont(font_1_path, cache_index=True, cache_chars=True),
                MicroFont(font_2_path, cache_index=True, cache_chars=True),
                MicroFont(font_3_path, cache_index=True, cache_chars=True)
            ]
            self.avail_fonts = len(self.fonts)
            print(f"[SimDisplay] Loaded {self.avail_fonts} bitmap fonts (12pt, 18pt, 32pt)")
        except Exception as e:
            print(f"[SimDisplay] Warning: Failed to load bitmap fonts: {e}")
            self.fonts = []
            self.avail_fonts = 0

        print(f"[SimDisplay] Window: {window_size[0]}x{window_size[1]} ({width}x{height} @ {scale}x scale)")

    def _draw_char_bitmap(self, char_data, ch_width, ch_height, x, y, scale=1):
        """
        Draw a character bitmap to the pygame surface.

        Args:
            char_data: Bytes object with character bitmap
            ch_width: Character width in pixels (actual, not padded)
            ch_height: Character height in pixels
            x, y: Position to draw
            scale: Scale factor (1, 2, 3, etc.)
        """
        # Calculate padded width (aligned to byte boundary)
        padded_width = ((ch_width + 7) // 8) * 8

        # Iterate through each pixel in the character bitmap
        for cy in range(ch_height):
            for cx in range(ch_width):  # Only iterate actual width, not padding
                # Calculate byte and bit position
                byte_idx = (padded_width // 8) * cy + (cx // 8)
                bit_idx = 7 - (cx % 8)

                # Check if pixel is set
                if byte_idx < len(char_data):
                    pixel_on = (char_data[byte_idx] >> bit_idx) & 1

                    if pixel_on:
                        # Draw pixel (or scaled block)
                        if scale == 1:
                            px = x + cx
                            py = y + cy
                            if 0 <= px < self.width and 0 <= py < self.height:
                                self.surface.set_at((px, py), self.pen_color)
                        else:
                            # Draw scaled block
                            px = x + (cx * scale)
                            py = y + (cy * scale)
                            for sy in range(scale):
                                for sx in range(scale):
                                    draw_x = px + sx
                                    draw_y = py + sy
                                    if 0 <= draw_x < self.width and 0 <= draw_y < self.height:
                                        self.surface.set_at((draw_x, draw_y), self.pen_color)

    def set_pen(self, r, g, b):
        """Set drawing color"""
        self.pen_color = (r, g, b)

    def rectangle(self, x, y, w, h):
        """Draw filled rectangle"""
        pygame.draw.rect(self.surface, self.pen_color, (x, y, w, h))

    def pixel(self, x, y):
        """Draw single pixel"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.surface.set_at((x, y), self.pen_color)

    def line(self, x1, y1, x2, y2):
        """Draw line"""
        pygame.draw.line(self.surface, self.pen_color, (x1, y1), (x2, y2))

    def text(self, text, x, y, scale=1):
        """
        Draw text using bitmap font.

        Args:
            text: String to draw
            x, y: Position
            scale: Font size (1=12pt, 2=18pt, 3=32pt)
        """
        if not self.fonts or self.avail_fonts == 0:
            return  # No fonts available

        # Select font based on scale - same logic as hardware
        if scale > self.avail_fonts:
            chosen_font = 0
        else:
            chosen_font = scale - 1

        font = self.fonts[chosen_font]

        # Track current x position
        cursor_x = x

        # Draw each character
        for char in str(text):
            if char == '\n':
                # Newline not handled in simple implementation
                continue

            # Get character bitmap data
            try:
                char_data, ch_height, ch_width = font.get_ch(char)

                # Draw character bitmap to surface (always scale=1 since font size is in the file)
                self._draw_char_bitmap(char_data, ch_width, ch_height, cursor_x, y, scale=1)

                # Advance cursor
                cursor_x += ch_width

            except Exception as e:
                # Skip characters that can't be rendered
                print(f"[SimDisplay] Warning: Failed to render character '{char}': {e}")
                continue

    def measure_text(self, text, scale=1):
        """
        Measure text width using bitmap font.

        Args:
            text: String to measure
            scale: Font size (1=12pt, 2=18pt, 3=32pt)

        Returns:
            Width in pixels
        """
        if not self.fonts or self.avail_fonts == 0:
            return 0

        # Select font based on scale - same logic as hardware
        if scale > self.avail_fonts:
            chosen_font = 0
        else:
            chosen_font = scale - 1

        font = self.fonts[chosen_font]

        # Same simple calculation as hardware for consistency
        return font.max_width * len(text)

    def update(self):
        """
        Update display - flip buffer to window.
        """
        # Scale surface to window if needed
        if self.scale > 1:
            scaled = pygame.transform.scale(
                self.surface,
                (self.width * self.scale, self.height * self.scale)
            )
            self.window.blit(scaled, (0, 0))
        else:
            self.window.blit(self.surface, (0, 0))

        # Flip display
        pygame.display.flip()

        # Note: Events are processed by SimKeyboard driver to avoid consuming them here

    def reset(self):
        """
        Reset display state - clear surface to black.

        This ensures a clean state for app transitions.
        """
        self.surface.fill((0, 0, 0))

    def cleanup(self):
        """Cleanup pygame and font resources"""
        # Clean up font file handles
        if hasattr(self, 'fonts') and self.fonts:
            for font in self.fonts:
                try:
                    if hasattr(font, 'stream') and font.stream:
                        font.stream.close()
                except:
                    pass
        pygame.quit()


# Singleton event pump for keyboard driver to use
_event_pump_called = False

def pump_events():
    """
    Pump pygame events.

    Called by keyboard driver to ensure events are processed.
    """
    global _event_pump_called
    if not _event_pump_called:
        pygame.event.pump()
        _event_pump_called = True

def reset_event_pump():
    """Reset event pump flag (called after each frame)"""
    global _event_pump_called
    _event_pump_called = False
