from slime_os.pico_calc_keyboard import Keyboard, PicoCalcKeyboard

if __name__ == "__main__":
    # Initialize the keyboard
    kbd = PicoCalcKeyboard()
    kbd.generate_interface()

    while True:
        # Read data from the keyboard
        data = kbd.get_data()
        print(data)