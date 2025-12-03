"""
Abstract display interface for Slime OS 2

All display drivers must implement this interface.
"""


class AbstractDisplay:
    """
    Abstract display interface

    Defines the contract that all display drivers must implement.
    """

    def __init__(self, width, height):
        """
        Initialize display.

        Args:
            width: Display width in pixels
            height: Display height in pixels
        """
        self.width = width
        self.height = height

    def get_bounds(self):
        """
        Get display dimensions.

        Returns:
            Tuple (width, height)
        """
        return (self.width, self.height)

    def set_pen(self, r, g, b):
        """
        Set current drawing color.

        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        raise NotImplementedError("Subclasses must implement set_pen()")

    def rectangle(self, x, y, w, h):
        """
        Draw filled rectangle.

        Args:
            x, y: Top-left corner position
            w, h: Width and height
        """
        raise NotImplementedError("Subclasses must implement rectangle()")

    def pixel(self, x, y):
        """
        Draw single pixel at current pen color.

        Args:
            x, y: Pixel position
        """
        raise NotImplementedError("Subclasses must implement pixel()")

    def line(self, x1, y1, x2, y2):
        """
        Draw line at current pen color.

        Args:
            x1, y1: Start position
            x2, y2: End position
        """
        raise NotImplementedError("Subclasses must implement line()")

    def text(self, text, x, y, scale=1):
        """
        Draw text at current pen color.

        Args:
            text: String to draw
            x, y: Position
            scale: Text scale (1, 2, 3, etc.)
        """
        raise NotImplementedError("Subclasses must implement text()")

    def measure_text(self, text, scale=1):
        """
        Measure text dimensions.

        Args:
            text: String to measure
            scale: Text scale

        Returns:
            Width in pixels
        """
        raise NotImplementedError("Subclasses must implement measure_text()")

    def update(self):
        """
        Update display - flip buffer to screen.

        For some displays this is a no-op (direct write).
        For buffered displays, this copies the buffer to the screen.
        """
        raise NotImplementedError("Subclasses must implement update()")

    def update_partial(self, x, y, w, h):
        """
        Update only a specific region of the display.

        For buffered displays, this copies only the specified region
        from the framebuffer to the screen. More efficient than full update.

        Args:
            x, y: Top-left corner of region to update
            w, h: Width and height of region

        Default implementation falls back to full update.
        Override for better performance.
        """
        self.update()

    def reset(self):
        """
        Reset display state - clear all buffers and queues.

        This should clear:
        - The display itself (to black)
        - Any framebuffers
        - Any text/drawing queues
        - Any cached state

        This is called during app transitions to ensure clean state.
        Default implementation does nothing (override if needed).
        """
        pass
