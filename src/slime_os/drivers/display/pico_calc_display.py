from slime_os.drivers.display.st7789 import ST7789Display
import st7789
from machine import SPI, Pin
from slime_os.device_config import my_device

class PicoCalcDisplay(ST7789Display):
    def __init__(self):
        # Initialize the ST7789 display with the appropriate parameters
        custom_init = [
            (b'\x01', 100),                  # soft reset
            (b'\xCF\x00\xC1\x30',),
            (b'\xED\x64\x03\x12\x81',),      # power on sequence control
            (b'\xE8\x85\x00\x78',),     # driver timing control A
            (b'\xCB\x39\x2C\x00\x34\x02',),  # power control A
            (b'\xF7\x20',),            # pump ratio control
            (b'\xEA\x00\x00',),     # driver timing control B
            (b'\xC0\x23',),            # power control,VRH[5:0]
            (b'\xC1\x10',),            # Power control,SAP[2:0];BT[3:0]
            (b'\xC5\x3E\x28',),        # vcm control
            (b'\xC7\x86',),            # vcm control 2
            (b'\x37\x00',),            # madctl
            (b'\x3A\x55',),            # pixel format
            (b'\xB1\x00\x18',),        # frameration control,normal mode full colours
            (b'\xB6\x02\x02',),       # display function control
            (b'\xF2\x00',),            # 3gamma function disable
            (b'\x26\x01',),            # gamma curve selected
            # set positive gamma correction
            (b'\xE0\x0F\x31\x2B\x0C\x0E\x08\x4E\xF1\x37\x07\x10\x03\x0E\x09\x00',),
            # set negative gamma correction
            (b'\xE1\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F',),
            (b'\x21', 50),    
            (b'\x11', 100),                  # display on
            (b'\x29', 100),                  # display on
        ]
    
        custom_rotations = [
            (0x88, 320, 320, 0, 0),
            (0xE8, 320, 320, 0, 0),
            (0x48, 320, 320, 0, 0),
            (0x28, 320, 320, 0, 0),
        ]
        spi = SPI(1, baudrate=40000000, sck=Pin(my_device.DISPLAY_SCK), mosi=Pin(my_device.DISPLAY_MOSI))
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
            buffer_size=buffer_size
        )

if __name__ == "__main__":
    display = PicoCalcDisplay()
    display.set_pen(255, 255, 255)  # Set pen color to red
    display.rectangle(0, 0, 100, 100)  # Draw a rectangle
    display.set_pen(0, 0, 255)  # Set pen color to blue
    display.pixel(50, 50)  # Draw a pixel
    display.line(0, 0, 100, 100)  # Draw a line
    display.text("Hello World", 10, 10, 1)  # Draw text
    display.update()  # Update the display to show the changes