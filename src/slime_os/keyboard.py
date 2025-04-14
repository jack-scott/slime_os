from slime_os.device_config import my_device

class Keyboard:
    def __init__(self, instance: str = None):
        if instance is None:
            instance = my_device.KEYBOARD_DRIVER
        self.is_ready = False
        if instance == "pico_calc":
            from slime_os.drivers.hid.pico_calc import PicoCalcKeyboard 
            self.driver = PicoCalcKeyboard()
        elif instance == "slime_deck":
            from slime_os.drivers.hid.slime_deck import SlimeDeckKeyboard
            self.driver = SlimeDeckKeyboard()
        else:
            raise ValueError("Invalid keyboard instance")

        self.initialize()

    def initialize(self):
        self.driver.initialize_interface()
        self.is_ready = True

    def get_key(self, key):
        if not self.is_ready:
            return False
        
        return self.driver.get_key(key)

    def get_keys(self, keys):            
        results = {}
        if not self.is_ready:
            return results
        
        for key in keys:
            results[key] = self.driver.get_key(key)
        
        return results
    
    def get_all(self):
        keys = []
        
        if not self.is_ready:
            return keys
        
        for key_type in self.driver.inv_keyboard_map:
            pressed  = self.get_key(key_type)
            if pressed:
                keys.append(key_type)
            
        return keys    


if __name__ == "__main__":
    # Initialize the keyboard
    import time
    from slime_os.keycode import keycode_as_str
    kbd = Keyboard()

    mapped_keys = kbd.driver.inv_keyboard_map
    for key in mapped_keys:
        print(f"Press {keycode_as_str[key]}")
        while True:
            pressed = kbd.get_key(key)
            if pressed:
                print(f"Got press")
                break
            time.sleep(0.1)

    print("All keys are working as expected")