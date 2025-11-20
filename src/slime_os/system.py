from slime_os.device_config import my_device
from slime_os.keyboard import Keyboard
from slime_os.graphics import Gfx
from slime_os.intents import *
from config import config as display_config

import os
import gc
from machine import Pin, I2C, UART, SPI

# import sdcard
from slime_os.launcher import HomeScreen
from slime_os.keycode import Keycode as keycode

def get_internal_i2c():
    return I2C(1, scl=Pin(my_device.KEYBOARD_SCL), sda=Pin(my_device.KEYBOARD_SDA))

# def get_sdcard():
#     sd_spi = SPI(0, sck=Pin(my_device.SD_CARD_SCK, Pin.OUT), mosi=Pin(my_device.SD_CARD_MOSI, Pin.OUT), miso=Pin(my_device.SD_CARD_MISO, Pin.OUT))
#     return sdcard.SDCard(sd_spi, Pin(my_device.SD_CARD_CS))

gfx = Gfx(my_device.DISPLAY_DRIVER)
kbd = Keyboard(my_device.KEYBOARD_DRIVER)

persist = {}

# sd = get_sdcard()
# os.mount(sd, "/sd")

def get_applications() -> list[dict[str, str, str]]:
    applications = []
    global app
    
    app_files = os.listdir()
    
    for file in app_files:
        if file.endswith("app.py"):
            applications.append({
                "file": file[:-3],
            })
            
    
    for app in applications:
        frontmatter = ""
        filename = app["file"] + ".py"
        with open(filename, 'r') as f:
            index = 0
            for line in f.readlines():
                if index == 0:
                    if not line.startswith("'"):
                        print(line)
                        print(f"[APP].MISSING_METADATA {name}")
                        break
                if index > 0:
                    if not line.startswith("'"):
                        frontmatter += line
                    else:
                        break
                index += 1
            f.close()
                
        try:
            exec(frontmatter)
        except SyntaxError:
            print(f"[APP].SYNTAX_ERROR {name}")

    return sorted(applications, key=lambda x: x["name"])

def draw_system_info():
    gfx.set_pen(*display_config["theme"]["black"])

    gfx.rectangle(0, gfx.dh - 40, gfx.dw, 40)
    gfx.set_pen(*display_config["theme"]["white"])
    gfx.line(gfx.dw-12, gfx.dh -40, gfx.dw-12-120, gfx.dh - 40)
    gfx.line(0+12,gfx.dh - 40, 0+12+120, gfx.dh - 40)
    
    window_title = "SLIMEDECK ZERO"
    gfx.text(window_title, gfx.dw-gfx.measure_text(window_title, scale=1), gfx.dh - 31)
    gfx.text(free(), 12, gfx.dh - 31)

def boot(next_app):
    for key,color in display_config["theme"].items():
        if isinstance(color, tuple):
            display_config["theme"][key] = gfx.set_pen(*color)
            
    running_app = next_app()
    running_app_instance = None

    while True:
        if running_app:
            if not running_app_instance:
                running_app.setup(gfx)
                running_app_instance = running_app.run()
            intent = next(running_app_instance)
        else:
            intent = INTENT_FLIP_BUFFER
            
        if is_intent(intent, INTENT_KILL_APP):
            running_app = None
            running_app_instance = None
            print("[SOS].APP_KILLED")
            gc.collect()
            
            next_app = HomeScreen
            if len(intent) == 2:
                next_app = __import__(intent[1]["file"]).App
            running_app = next_app()
            
        if is_intent(intent, INTENT_NO_OP):
            pass
        
        
        if is_intent(intent, INTENT_FLIP_BUFFER):
            draw_system_info()
            gfx.update()

def prepare_for_launch() -> None:
    for k in locals().keys():
        if k not in ("__name__",
                     "gc"):
            del locals()[k]
    gc.collect()
    
def free(full=False):
    gc.collect()
    F = gc.mem_free()
    A = gc.mem_alloc()
    T = F+A
    P = 'MEM USAGE {0:.2f}%'.format(100-(F/T*100))
    if not full: return P
    else : return ('T:{0} F:{1} ({2})'.format(T,F,P))

