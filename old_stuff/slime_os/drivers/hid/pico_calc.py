from slime_os.keycode import Keycode
from machine import Pin, I2C
from slime_os.drivers.hid.abstract_keyboard import AbstractKeyboard
from slime_os.device_config import my_device
import time

class PicoCalcKeyboard(AbstractKeyboard):   
    kbd_map = {
        111: Keycode.O,
        112: Keycode.P,
        113: Keycode.Q,
        114: Keycode.R,
        115: Keycode.S,
        116: Keycode.T,
        117: Keycode.U,
        118: Keycode.V,
        119: Keycode.W,
        8: Keycode.BACKSPACE,
        9: Keycode.TAB,
        10: Keycode.RETURN,
        44: Keycode.COMMA,
        46: Keycode.PERIOD,
        47: Keycode.KEYPAD_FORWARD_SLASH,
        122: Keycode.Z,
        120: Keycode.X,
        121: Keycode.Y,
        106: Keycode.J,
        107: Keycode.K,
        108: Keycode.L,
        109: Keycode.M,
        110: Keycode.N,
        97: Keycode.A,
        98: Keycode.B,
        99: Keycode.C,
        100: Keycode.D,
        101: Keycode.E,
        102: Keycode.F,
        103: Keycode.G,
        104: Keycode.H,
        105: Keycode.I,
        32: Keycode.SPACE,
        180: Keycode.LEFT_ARROW,
        181: Keycode.UP_ARROW,
        183: Keycode.RIGHT_ARROW,
        182: Keycode.DOWN_ARROW
    }

    def __init__(self):
        super().__init__(self.kbd_map)
        self.i2c = None
        self.held = {}
        self.time_of_key = 0
        self.key_held_timeout = 500
        self.keys_on_list = []
        for key in self.keyboard_map:
            self.held[key] = False

    def initialize_interface(self):
        scl=Pin(my_device.KEYBOARD_SCL,Pin.IN,Pin.PULL_UP)
        sda=Pin(my_device.KEYBOARD_SDA,Pin.IN,Pin.PULL_UP)
        self.i2c = I2C(1, scl=scl, sda=sda, freq=10000)

    def get_data(self):
        self.i2c.writeto(31, b'\x09')
        time.sleep_ms(16)
        data = self.i2c.readfrom(31, 2)
        buff = (data[1] << 8) | data[0]  # Combine bytes into 16-bit value
        if buff != 0:
            # Parse the data
            action_code = buff & 0xFF
            key_code = buff >> 8
            if action_code == 1:  # Key pressed
                return key_code
            elif action_code == 3:  # Key released
                return -key_code
        
        return 0
    
    def clear_held_keys(self):
        for key in self.keys_on_list:
            self.held[key] = False
        self.keys_on_list = []
        self.time_of_key = 0

    def set_or_clear_key(self, key):
        if key < 0: #Key is released
            key = -key
            if key in self.keys_on_list:
                self.keys_on_list.remove(key)
            self.held[key] = False
        else: #Key is pressed
            if key not in self.keys_on_list:
                self.keys_on_list.append(key)
            self.held[key] = True
        self.time_of_key = time.ticks_ms()
        
    def get_key(self, key):
        expected_val = self.inv_keyboard_map.get(key, None)
        if expected_val is None:
            return False
        
        received_val = self.get_data()
        if received_val == 0 and self.time_of_key != 0:
            if time.ticks_diff(time.ticks_ms(), self.time_of_key) > self.key_held_timeout:
                self.clear_held_keys()
        else:
            # Got a either a key press or release
            self.set_or_clear_key(received_val)
        
        return self.held[expected_val] 


if __name__ == "__main__":
    # Map desired keys to thier raw data
    import time
    from slime_os.keycode import keycode_as_str
    raw_kbd = PicoCalcKeyboard()
    raw_kbd.initialize_interface()

    output_mapping = {}
    zeros= 0
    last_print = 0
    time_between_prints = 2000
    # while True:
    #     tick = time.ticks_ms()
    #     raw_data = raw_kbd.get_data()
    #     if raw_data != 0:
    #         print(f"Raw data: {raw_data}, zeros: {zeros}")
    #         zeros = 0
    #     else:
    #         zeros += 1

    #     tock = time.ticks_ms()
    #     #print loop speed
    #     if (tock - last_print) > time_between_prints:
    #         last_print = tock
    #         print(f"Loop time: {tock - tick}ms")



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
