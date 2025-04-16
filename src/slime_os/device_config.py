

# Leave your desired device config uncommented here

# For pico_calc
class DeviceConfig:
    def __init__(self):
        # EXPANSION I2C
        self.EXPANSION_SCL = 1
        self.EXPANSION_SDA = 0
        # EXPANSION UART
        self.EXPANSION_UART_TX = 0
        self.EXPANSION_UART_RX = 1
        # SD CARD SPI
        self.SD_CARD_SCK = 18
        self.SD_CARD_MOSI = 19
        self.SD_CARD_MISO = 16
        self.SD_CARD_CS = 17 # TODO: Double check this is actually used as a CS pin
        # KEYBOARD
        self.KEYBOARD_SCL = 7
        self.KEYBOARD_SDA = 6
        # KEYBOARD DRIVER
        self.KEYBOARD_DRIVER = "pico_calc"
        
        # DISPLAY
        self.DISPLAY_WIDTH = 320
        self.DISPLAY_HEIGHT = 320
        self.DISPLAY_CS = 13
        self.DISPLAY_DC = 14
        self.DISPLAY_SCK = 10
        self.DISPLAY_MOSI = 11
        self.DISPLAY_RESET = 15
        self.DISPLAY_DRIVER = "pico_calc"

        ## UNKNOWN ENUMS ##
        # EXPANSION UART
        self.CTRL_UART_9600 = 0
        self.CTRL_UART_115200 = 1
        self.CTRL_UART_STANDARD = self.CTRL_UART_9600
        self.CTRL_UART_FAST = self.CTRL_UART_115200
        # EXPANSION I2C
        self.CTRL_I2C_STANDARD = 10
        self.CTRL_I2C_FAST = 11

my_device = DeviceConfig()
# For slime_deck
# class DeviceConfig:
#     def __init__(self):
        # EXPANSION I2C
        # self.EXPANSION_SCL = 1
        # self.EXPANSION_SDA = 0
        # # EXPANSION UART
        # self.EXPANSION_UART_TX = 0
        # self.EXPANSION_UART_RX = 1
        # # SD CARD SPI
        # self.SD_CARD_SCK = 10
        # self.SD_CARD_MOSI = 11
        # self.SD_CARD_MISO = 12
        # self.SD_CARD_CS = 15 # TODO: Double check this is actually used as a CS pin
        # # KEYBOARD
        # self.KEYBOARD_SCL = 7
        # self.KEYBOARD_SDA = 6
        # # KEYBOARD DRIVER
        # self.KEYBOARD_DRIVER = "slime_deck"
        
        # ## UNKNOWN ENUMS ##
        # # EXPANSION UART
        # self.CTRL_UART_9600 = 0
        # self.CTRL_UART_115200 = 1
        # self.CTRL_UART_STANDARD = self.CTRL_UART_9600
        # self.CTRL_UART_FAST = self.CTRL_UART_115200
        # # EXPANSION I2C
        # self.CTRL_I2C_STANDARD = 10
        # self.CTRL_I2C_FAST = 11