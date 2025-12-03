from slime_os.drivers.display.st7789 import ST7789Display
import st7789
from machine import SPI, Pin
from slime_os.device_config import my_device
import framebuf

class PicoCalcDisplay(ST7789Display):
    def __init__(self):
        # Initialize the ST7789 display with the appropriate parameters
        custom_init = [
            (b'\x01', 100),  # Soft reset (if hardware reset isn't available)
            
            # Gamma settings
            (b'\xE0\x00\x03\x09\x08\x16\x0A\x3F\x78\x4C\x09\x0A\x08\x16\x1A\x0F',),
            (b'\xE1\x00\x16\x19\x03\x0F\x05\x32\x45\x46\x04\x0E\x0D\x35\x37\x0F',),
            
            # Power control
            (b'\xC0\x17\x15',),
            (b'\xC1\x41',),
            (b'\xC5\x00\x12\x80',),
            
            # Memory access control
            (b'\x36\x48',),  # MADCTL (0x36) with MX/BGR settings
            
            # Interface configuration
            (b'\x3A\x55',),  # Pixel format: 16-bit color 
            (b'\xB0\x00',),  # Interface mode control
            (b'\xB1\xA0',),  # Frame rate control
            
            # Display features
            (b'\x21',),      # Display inversion ON (INVON)
            (b'\xB4\x02',),  # Display inversion control
            (b'\xB6\x02\x02\x3B',),  # Display function control
            
            # Additional controls
            (b'\xB7\xC6',),  # Entry mode set
            (b'\xE9\x00',),
            (b'\xF7\xA9\x51\x2C\x82',),
            
            # Wakeup sequence
            (b'\x11', 120),  # Sleep OUT (SLPOUT)
            (b'\x29', 120),  # Display ON (DISPON)
        ]
    
        custom_rotations = [
            (0x88, 320, 320, 0, 0),
            (0xE8, 320, 320, 0, 0),
            (0x48, 320, 320, 0, 0),
            (0x28, 320, 320, 0, 0),
        ]
        spi = SPI(1, baudrate=80000000, sck=Pin(my_device.DISPLAY_SCK), mosi=Pin(my_device.DISPLAY_MOSI))
        rotation = 2
        colour_order = st7789.RGB
        inversion = False
        options = 0
        buffer_size = 0
        super().__init__(
            width=my_device.DISPLAY_WIDTH,
            height=my_device.DISPLAY_HEIGHT,
            spi=spi,
            cs=Pin(my_device.DISPLAY_CS, Pin.OUT),
            dc=Pin(my_device.DISPLAY_DC, Pin.OUT),
            reset=Pin(my_device.DISPLAY_RESET, Pin.OUT),
            custom_init=custom_init,
            custom_rotations=custom_rotations,
            rotation=rotation,
            color_order=colour_order,
            inversion=inversion,
            options=options,
            buffer_size=buffer_size,
            backlight=Pin(my_device.DISPLAY_BACKLIGHT, Pin.OUT),
        )
        self.fbuf_w = 320
        self.fbuf_h = 100
        self.fbuf = framebuf.FrameBuffer(bytearray(self.fbuf_w * self.fbuf_h * 2), self.fbuf_w, self.fbuf_h, framebuf.RGB565)
        self.fbuf.fill(0)  # Clear the framebuffer

    def set_pen_fb(self, r, g, b):
        """
        Sets the pen color for drawing.
        """
        msb_colour = st7789.color565(r, g, b)
        lsb_colour = (msb_colour >> 8) | ((msb_colour & 0xff) << 8)
        self.current_pen = lsb_colour

    def rectangle_fb(self, x, y, w, h):
        """
        Draws a rectangle on the framebuffer.
        """
        self.fbuf.rect(x, y, w, h, self.current_pen, 1)
    
    def pixel_fb(self, x, y):
        """
        Draws a pixel on the framebuffer.
        """
        self.fbuf.pixel(x, y, self.current_pen)

    def line_fb(self, x1, y1, x2, y2, t=1):
        """
        Draws a line on the framebuffer.
        """
        self.fbuf.line(x1, y1, x2, y2, self.current_pen)

    def update(self):
        return self.display.blit_buffer(self.fbuf, 0, 0, self.fbuf_w, self.fbuf_h)


if __name__ == "__main__":
    display = PicoCalcDisplay()
    iters = 50
    increment = 320 // iters
    colour_increment = 255 // iters
    # while True:
    #     for j in range(iters):
    #         blue = j * colour_increment
    #         for i in range(iters):
    #             red = i * colour_increment
    #             display.set_pen(red, 0, blue)  # Set pen color to red
    #             display.rectangle(i * increment, 0, increment, 100)  # Draw a rectangle
    #             display.set_pen(0, i * colour_increment, 0)  # Set pen color to green
    #             # display.pixel(i * increment + (increment // 2), i * increment + (increment // 2))  # Draw a pixel
    #             # display.line(i * increment, i * increment, (i + 1) * increment, (i + 1) * increment)  # Draw a line
    #         display.set_pen(255, 255, 255)
    #         display.rectangle(j * increment, 0, increment, 100)


    blue = 0
    j = 0
    while True:
        for j in range(iters):
            blue = j * colour_increment
            for i in range(iters):
                red = i * colour_increment
                display.set_pen_fb(red, 0, blue)  # Set pen color to red
                display.rectangle_fb(i * increment, 0, increment, 100)  # Draw a rectangle
                # display.set_pen(0, i * colour_increment, 0)  # Set pen color to green
                # display.pixel_fb(i * increment + (increment // 2), i * increment + (increment // 2))  # Draw a pixel
                # display.line_fb(i * increment, i * increment, (i + 1) * increment, (i + 1) * increment)  # Draw a line
            display.set_pen_fb(255, 255, 255)
            display.rectangle_fb(j * increment, 0, increment, 100)        
            display.update()
        # display.update()  # Update the display to show the changes
    # for i in range(10):
    #     display.rectangle(0, 0, 320, 320)  # Clear the display
    #     display.set_pen(255, 255, 255)  # Set pen color to red
    #     display.rectangle(0, 0, 100, 100)  # Draw a rectangle
    #     display.set_pen(0, 0, 255)  # Set pen color to blue
    #     display.pixel(50, 50)  # Draw a pixel
    #     display.line(0, 0, 100, 100)  # Draw a line
    #     # display.text("Hello World", 10, 10, 1)  # Draw text
    #     # display.update()  # Update the display to show the changes