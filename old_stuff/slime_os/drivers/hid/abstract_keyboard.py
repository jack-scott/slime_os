class AbstractKeyboard:
    def __init__(self, keyboard_map):
        self.keyboard_map = keyboard_map
        self.inv_keyboard_map = {}
        for key, value in keyboard_map.items():
            self.inv_keyboard_map[value] = key

    def intialize_interface(self):
        """
        Generates the interface for the keyboard.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def get_key(self, key):
        """
        Returns True if the key is pressed, False otherwise.
        """
        raise NotImplementedError("Subclasses should implement this method.")

