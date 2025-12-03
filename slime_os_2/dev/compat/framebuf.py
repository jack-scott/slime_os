"""
Stub implementation of framebuf module

Provides minimal FrameBuffer class for compatibility.
Not used in simulator (SimDisplay uses pygame directly).
"""


RGB565 = 1


class FrameBuffer:
    """Stub FrameBuffer class"""

    def __init__(self, buffer, width, height, format):
        self.buffer = buffer
        self.width = width
        self.height = height
        self.format = format

    def fill(self, color):
        pass

    def pixel(self, x, y, color=None):
        if color is None:
            return 0
        pass

    def rect(self, x, y, w, h, color, fill=0):
        pass

    def line(self, x1, y1, x2, y2, color):
        pass
