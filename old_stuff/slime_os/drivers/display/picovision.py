from slime_os.drivers.display.abstract_display import AbstractDisplay
from picovision import PicoVision, PEN_P5
# display = PicoVision(PEN_P5, 400, 240)

class PicoVisionDisplay(AbstractDisplay):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.pen = PEN_P5
        self.display = PicoVision(pen, width, height)
        self.width = width
        self.height = height

    
    def set_pen(self, r, g, b):
        """
        Sets the pen color for drawing.
        """
        self.display.set_pen(r, g, b)

    def rectangle(self, x, y, w, h):
        """
        Draws a rectangle on the display.
        """
        self.display.rectangle(x, y, w, h)

    def pixel(self, x, y):
        """
        Draws a pixel on the display.
        """
        self.display.pixel(x, y)

    def line(self, x, y, x2, y2, t=1):
        """
        Draws a line on the display.
        """
        self.display.line(x, y, x2, y2, t)

    def text(self, text, x, y, scale=1, angle=0):
        """
        Draws text on the display.
        """
        self.display.text(text, x, y, scale=scale, angle=angle)

    def measure_text(self, text, scale=1):
        """
        Measures the size of the text.
        """
        return self.display.measure_text(text, scale=scale)
    
    def update(self):
        """
        Updates the display.
        """
        self.display.update()