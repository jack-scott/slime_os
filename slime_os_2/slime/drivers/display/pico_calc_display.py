"""
Pico Calc Display Driver

Hardware: 320x320 ST7789 LCD over SPI
Uses framebuffer for improved performance
"""

from .abstract import AbstractDisplay
import st7789
import framebuf
from machine import SPI, Pin
import gc
# Import font - romanp is the standard 8x8 font
try:
    import romanp as font
except ImportError:
    print("[Display] Warning: romanp font not found, text rendering may fail")
    font = None


class PicoCalcDisplay(AbstractDisplay):
    """
    Pico Calc 320x320 ST7789 display driver

    Uses a partial framebuffer (320x100 pixels) for better performance
    while staying within memory constraints.
    """

    def __init__(self, width, height, sck, mosi, cs, dc, reset, backlight):
        """
        Initialize Pico Calc display.

        Args:
            width, height: Display dimensions (should be 320x320)
            sck, mosi: SPI pins
            cs, dc, reset, backlight: Display control pins
        """
        super().__init__(width, height)

        # Custom initialization sequence for Pico Calc's display
        custom_init = [
            (b'\x01', 100),  # Soft reset
            # Gamma settings
            (b'\xE0\x00\x03\x09\x08\x16\x0A\x3F\x78\x4C\x09\x0A\x08\x16\x1A\x0F',),
            (b'\xE1\x00\x16\x19\x03\x0F\x05\x32\x45\x46\x04\x0E\x0D\x35\x37\x0F',),
            # Power control
            (b'\xC0\x17\x15',),
            (b'\xC1\x41',),
            (b'\xC5\x00\x12\x80',),
            # Memory access control
            (b'\x36\x48',),  # MADCTL with MX/BGR settings
            # Interface configuration
            (b'\x3A\x55',),  # 16-bit color
            (b'\xB0\x00',),  # Interface mode control
            (b'\xB1\xA0',),  # Frame rate control
            # Display features
            (b'\x21',),  # Display inversion ON
            (b'\xB4\x02',),  # Display inversion control
            (b'\xB6\x02\x02\x3B',),  # Display function control
            # Additional controls
            (b'\xB7\xC6',),
            (b'\xE9\x00',),
            (b'\xF7\xA9\x51\x2C\x82',),
            # Wakeup
            (b'\x11', 120),  # Sleep OUT
            (b'\x29', 120),  # Display ON
        ]

        # Custom rotations for this display
        custom_rotations = [
            (0x88, 320, 320, 0, 0),
            (0xE8, 320, 320, 0, 0),
            (0x48, 320, 320, 0, 0),
            (0x28, 320, 320, 0, 0),
        ]

        # Initialize SPI
        spi = SPI(1, baudrate=80_000_000, sck=Pin(sck), mosi=Pin(mosi))

        # Initialize ST7789 driver
        self.display = st7789.ST7789(
            spi,
            width,
            height,
            cs=Pin(cs, Pin.OUT),
            dc=Pin(dc, Pin.OUT),
            reset=Pin(reset, Pin.OUT),
            backlight=Pin(backlight, Pin.OUT),
            custom_init=custom_init,
            rotations=custom_rotations,
            rotation=2,  # 180 degree rotation
            color_order=st7789.RGB,
            inversion=False,
            options=0,
            buffer_size=0
        )

        # Initialize display
        self.display.init()
        self.display.on()
        self.display.fill(0)  # Clear to black

        # Font
        self.font = font

        # Current pen color (RGB565 format)
        self.current_pen = st7789.color565(255, 255, 255)  # White

        # Framebuffer for improved performance
        # 320x100 pixels = 64KB (fits in RAM)
        self.fbuf_w = 320
        self.fbuf_h = 320
        self.fbuf = framebuf.FrameBuffer(
            bytearray(self.fbuf_w * self.fbuf_h * 2),
            self.fbuf_w,
            self.fbuf_h,
            framebuf.RGB565
        )
        self.fbuf.fill(0)  # Clear framebuffer
        self.text_queue = []


    def set_pen(self, r, g, b):
        """Set drawing color"""
        self._set_pen_fb(r,g,b)
        self.current_pen = st7789.color565(r, g, b)

    def rectangle(self, x, y, w, h):
        """Draw filled rectangle"""
        self._rectangle_fb(x,y,w,h)

    def pixel(self, x, y):
        """Draw single pixel"""
        self._pixel_fb(x,y)

    def line(self, x1, y1, x2, y2):
        """Draw line"""
        self._line_fb(x1,y1,x2,y2)

    def text(self, text, x, y, scale=1):
        """Draw text"""
        # pass
        if self.font is None:
            return  # No font available
        self._queue_text(text, x, y, self.current_pen, scale)

    def measure_text(self, text, scale=1):
        """Measure text width"""
        if self.font is None:
            return 0
        return self.display.draw_len(self.font, text, scale)

    def update(self):
        """
        Update display - blit framebuffer to screen.

        Note: Currently drawing directly to display, so this is a no-op.
        Framebuffer methods (below) can be used for improved performance.
        """
        self._blit_framebuffer()
        # Draw queued text
        for text, x, y, color, scale in self.text_queue:
            self.display.draw(self.font, text, x, y, color, scale)
        
        self.text_queue.clear()

    # ========================================================================
    # Framebuffer methods (optional, for performance)
    # ========================================================================

    def _queue_text(self, text, x, y, color, scale):
        self.text_queue.append((text, x, y, color, scale))
        print(f"Queued text: {text}, {x}, {y}, {color}, {scale}")
        print(f"Remaining ram: {gc.mem_free()}")

    def _set_pen_fb(self, r, g, b):
        """Set pen color for framebuffer drawing"""
        msb_colour = st7789.color565(r, g, b)
        lsb_colour = (msb_colour >> 8) | ((msb_colour & 0xFF) << 8)
        self.current_pen_fb = lsb_colour

    def _rectangle_fb(self, x, y, w, h):
        """Draw filled rectangle to framebuffer"""
        self.fbuf.rect(x, y, w, h, self.current_pen_fb, 1)

    def _pixel_fb(self, x, y):
        """Draw pixel to framebuffer"""
        self.fbuf.pixel(x, y, self.current_pen_fb)

    def _line_fb(self, x1, y1, x2, y2):
        """Draw line to framebuffer"""
        self.fbuf.line(x1, y1, x2, y2, self.current_pen_fb)

    def _blit_framebuffer(self, x=0, y=0):
        """Blit framebuffer to display at position"""
        return self.display.blit_buffer(self.fbuf, x, y, self.fbuf_w, self.fbuf_h)
