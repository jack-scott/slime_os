from slime_os.keycode import Keycode
from machine import Pin, I2C


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

kbd_map_inv = {}

for key,value in kbd_map.items():
    kbd_map_inv[value] = key

class AbstractKeyboard:
    def __init__(self):
        pass

    def generate_interface(self):
        pass

    def get_data(self):
        pass

class PicoCalcKeyboard(AbstractKeyboard):    
    def __init__(self):
        super().__init__()
        self.i2c = None

    def generate_interface(self):
        scp=Pin(7,Pin.IN,Pin.PULL_UP)
        sdp=Pin(6,Pin.IN,Pin.PULL_UP)
        self.i2c = I2C(1, scl=scp, sda=sdp, freq=10000)

    def get_data(self):
        byte_data = self.i2c.readfrom_mem(31, 0x09,2)
        # Convert the byte data to an integer
        data = int.from_bytes(byte_data, 'big')
        return data


class Keyboard:
    def __init__(self, interface):
        self.is_ready = False
        self.kbd = interface
        try:
            self.kbd.generate_interface()
            self.is_ready=True
        except OSError as e:
            print("[KBD].error:", e)
            self.is_ready=False
            
        self.held = {}

        for key in kbd_map:
            self.held[key] = False

        if self.is_ready:
            print("[KBD].ready")
        else:
            print("[KBD].not_ready")
            
    def get_key(self, key):
        expected_val = kbd_map_inv[key]
        
        received = self.kbd.get_data()
        pressed = False
        
        if received == expected_val:
            if not self.held[expected_val]:
                pressed = True
            self.held[expected_val] = True
        else:
            self.held[expected_val] = False
        
        return pressed
    
    def get_keys(self, keys):
        results = {}
        
        for key in keys:
            results[key] = self.get_key(key)
        
        return results
    
    def get_all(self):
        keys = []
        
        if not self.is_ready:
            return keys
        
        for key_type in kbd_map_inv:
            pressed  = self.get_key(key_type)
            if pressed:
                keys.append(key_type)
            
        return keys    


if __name__ == "__main__":
    # Initialize the keyboard
    import time
    from slime_os.keycode import keycode_as_str
    raw_kbd = PicoCalcKeyboard()
    kbd = Keyboard(raw_kbd)
    # kbd.generate_interface()

    # output_mapping = {}

    # for key in kbd_map_inv:
    #     print(f"Press {keycode_as_str[key]} to map")
    #     while True:
    #         raw_data = raw_kbd.get_data()
    #         if raw_data != 0:
    #             print("Raw data:", raw_data)
    #             output_mapping[raw_data] = keycode_as_str[key]
    #             print(f"Mapped {keycode_as_str[key]} to {hex(raw_data)}")
    #             time.sleep(0.5)

    #             for i in range(5):
    #                 raw_data = raw_kbd.get_data()
    #             time.sleep(0.5)
                
    #             break
    #         time.sleep(0.01)


    # print("Output mapping:")
    # print(output_mapping)
    while True:
        # Read data from the keyboard
        # raw_data = raw_kbd.get_data()
        raw_data = False
        # key_data = kbd.get_all()
        key_data = False
        # is_q, q_held = kbd.get_key(Keycode.Q)
        raw_data = raw_kbd.get_data()
        if raw_data != 0:
            raw_data = raw_data
            raw_key = kbd_map.get(raw_data)
            key_str = keycode_as_str.get(raw_key)
            print(f"Raw data: {raw_data} key val: {raw_key} {key_str}")
        # print(raw_kbd.get_data())
        # print(f"Raw hex: {raw_data}, Key: {key_data} Q: {is_q} {q_held}")
        time.sleep(0.1)