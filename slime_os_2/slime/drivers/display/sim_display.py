"""
Simulator Display Driver

Pygame-based virtual display for running Slime OS on desktop.
"""

from .abstract import AbstractDisplay

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

        # Font for text rendering
        # Use a monospace font, size 8 to approximate hardware font
        try:
            # Try to use a nice monospace font
            self.font_cache = {}
            self._load_font(1)  # Pre-load scale 1
        except:
            print("[SimDisplay] Warning: Font loading failed")

        print(f"[SimDisplay] Window: {window_size[0]}x{window_size[1]} ({width}x{height} @ {scale}x scale)")

    def _load_font(self, scale):
        """Load font for given scale (cached)"""
        if scale not in self.font_cache:
            size = 8 * scale
            # Try monospace fonts
            for font_name in ['DejaVuSansMono', 'Courier', 'Monaco', None]:
                try:
                    self.font_cache[scale] = pygame.font.SysFont(font_name, size)
                    break
                except:
                    continue

            # Fallback to default
            if scale not in self.font_cache:
                self.font_cache[scale] = pygame.font.Font(None, size)

        return self.font_cache[scale]

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
        Draw text.

        Args:
            text: String to draw
            x, y: Position
            scale: Text scale (1, 2, 3, etc.)
        """
        font = self._load_font(scale)

        # Render text
        text_surface = font.render(str(text), True, self.pen_color)
        self.surface.blit(text_surface, (x, y))

    def measure_text(self, text, scale=1):
        """
        Measure text width.

        Returns:
            Width in pixels
        """
        font = self._load_font(scale)
        width, height = font.size(str(text))
        return width

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
        """Cleanup pygame resources"""
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
