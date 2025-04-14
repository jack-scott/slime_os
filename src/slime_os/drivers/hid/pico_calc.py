from slime_os.keycode import Keycode
from machine import Pin, I2C
from slime_os.drivers.hid.abstract_keyboard import AbstractKeyboard

class PicoCalcKeyboard(AbstractKeyboard):   
    kbd_map = {
        353: Keycode.A,
        354: Keycode.B,
        355: Keycode.C,
        356: Keycode.D,
        357: Keycode.E,
        358: Keycode.F,
        359: Keycode.G,
        360: Keycode.H,
        361: Keycode.I,
        362: Keycode.J,
        363: Keycode.K,
        364: Keycode.L,
        366: Keycode.N,
        365: Keycode.M,
        367: Keycode.O,
        368: Keycode.P,
        369: Keycode.Q,
        370: Keycode.R,
        371: Keycode.S,
        372: Keycode.T,
        373: Keycode.U,
        374: Keycode.V,
        375: Keycode.W,
        376: Keycode.X,
        377: Keycode.Y,
        378: Keycode.Z,
        302: Keycode.PERIOD,
        288: Keycode.SPACE,
        300: Keycode.COMMA,
        264: Keycode.BACKSPACE,
        265: Keycode.TAB,
        266: Keycode.RETURN,
        303: Keycode.KEYPAD_FORWARD_SLASH,
        436: Keycode.LEFT_ARROW,
        439: Keycode.RIGHT_ARROW,
        437: Keycode.UP_ARROW,
        438: Keycode.DOWN_ARROW,
    }

    def __init__(self):
        super().__init__(self.kbd_map)
        self.i2c = None
        self.held = {}

        for key in self.keyboard_map:
            self.held[key] = False

    def initialize_interface(self):
        scl=Pin(7,Pin.IN,Pin.PULL_UP)
        sda=Pin(6,Pin.IN,Pin.PULL_UP)
        self.i2c = I2C(1, scl=scl, sda=sda, freq=10000)

    def get_data(self):
        byte_data = self.i2c.readfrom_mem(31, 0x09,2)
        # Convert the byte data to an integer
        data = int.from_bytes(byte_data, 'big')
        return data

    def get_key(self, key):
        expected_val = self.inv_keyboard_map.get(key, None)
        if expected_val is None:
            return False
        
        received_val = self.get_data()
        pressed = False
        
        if received_val == expected_val:
            if not self.held[expected_val]:
                pressed = True
            self.held[expected_val] = True
        else:
            self.held[expected_val] = False
        
        return pressed


if __name__ == "__main__":
    # Map desired keys to thier raw data
    import time
    from slime_os.keycode import keycode_as_str
    raw_kbd = PicoCalcKeyboard()
    raw_kbd.initialize_interface()

    output_mapping = {}

    for key in raw_kbd.inv_keyboard_map:
        print(f"Press {keycode_as_str[key]} to map")
        while True:
            raw_data = raw_kbd.get_data()
            if raw_data != 0:
                print("Raw data:", raw_data)
                output_mapping[raw_data] = keycode_as_str[key]
                print(f"Mapped {keycode_as_str[key]} to {hex(raw_data)}")
                time.sleep(0.5)

                for i in range(5):
                    raw_data = raw_kbd.get_data()
                time.sleep(0.5)
                
                break
            time.sleep(0.01)


    print("Output mapping:")
    print(output_mapping)
