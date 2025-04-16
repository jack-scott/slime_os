from slime_os.drivers.display.abstract_display import AbstractDisplay
import st7789
import romanp as imported_font
from machine import SPI, Pin, freq

class ST7789Display(AbstractDisplay):
    def __init__(self, width, height, spi, cs, dc, reset, custom_init=None, custom_rotations=None, rotation=2, color_order=st7789.RGB, inversion=False, options=0, buffer_size=0):
        super().__init__(width, height)
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.reset = reset
        self.custom_init = custom_init
        self.custom_rotations = custom_rotations
        self.rotation = rotation
        self.color_order = color_order
        self.inversion = inversion
        self.options = options

        self.display = st7789.ST7789(
            self.spi,
            width,
            height,
            cs=self.cs,
            dc=self.dc,
            reset=self.reset,
            custom_init=self.custom_init,
            rotation=self.rotation,
            color_order=self.color_order,
            inversion=self.inversion,
            options=self.options,
            rotations=self.custom_rotations,
            buffer_size=buffer_size
        )
        self.display.init()
        self.display.fill(0)

        self.default_pen = st7789.color565(255, 255, 255)  # White
        self.default_font = imported_font
        self.font = self.default_font
        self.current_pen = self.default_pen

    def set_pen(self, r, g, b):
        """
        Sets the pen color for drawing.
        """ 
        self.current_pen = st7789.color565(r, g, b)

    def rectangle(self, x, y, w, h):
        """
        Draws a rectangle on the display.
        """
        self.display.fill_rect(x, y, w, h, self.current_pen)


    def pixel(self, x, y):
        """
        Draws a pixel on the display.
        """
        self.display.pixel(x, y, self.current_pen)


    def line(self, x, y, x2, y2, t=1):
        """
        Draws a line on the display.
        """
        if t != 1:
            pass
            # raise NotImplementedError("Line thickness not supported in ST7789 driver.")
        self.display.line(x, y, x2, y2, self.current_pen)


    def text(self, text, x, y, scale=1, angle=0):
        """
        Draws text on the display.
        """
        if angle != 0:
            raise NotImplementedError("Text rotation not supported in ST7789 driver.")

        self.display.draw(self.font, text, x ,y, self.current_pen, scale)

    def measure_text(self, text, scale=1):
        """
        Measures the size of the text.
        """
        return self.display.draw_len(self.font, text, scale)

    def update(self):
        """
        Updates the display.
        """
        pass # This driver writes directly to the display, so no update is needed. 