from slime_os.device_config import my_device
from slime_os.keyboard import Keyboard
from slime_os.graphics import Gfx
from slime_os.expansion import Ctrl
from slime_os.intents import *
from config import config as display_config

import os
import gc
from machine import Pin, I2C, UART, SPI

import sdcard
from slime_os.launcher import HomeScreen
from slime_os.keycode import Keycode as keycode

def get_internal_i2c():
    return I2C(1, scl=Pin(my_device.KEYBOARD_SCL), sda=Pin(my_device.KEYBOARD_SDA))

def get_expansion_i2c():
    return I2C(1, scl=Pin(my_device.EXPANSION_SCL), sda=Pin(my_device.EXPANSION_SDA))

def get_expansion_uart(baudrate=115200):
    return UART(0, baudrate, tx=Pin(my_device.EXPANSION_UART_TX), rx=Pin(my_device.EXPANSION_UART_RX))
    
def get_sdcard():
    sd_spi = SPI(0, sck=Pin(my_device.SD_CARD_SCK, Pin.OUT), mosi=Pin(my_device.SD_CARD_MOSI, Pin.OUT), miso=Pin(my_device.SD_CARD_MISO, Pin.OUT))
    return sdcard.SDCard(sd_spi, Pin(my_device.SD_CARD_CS))

gfx = Gfx(my_device.DISPLAY_DRIVER)
ctrl = Ctrl(gfx)
kbd = Keyboard(my_device.KEYBOARD_DRIVER)

persist = {}

sd = get_sdcard()
os.mount(sd, "/sd")
TMP_DOWNLOAD_PLAY_APP = "/sd/download_play_app.py"
try:
    os.remove(TMP_DOWNLOAD_PLAY_APP)
    print("[sos].temp_file_removed")
except:
    print("[sos].temp_file_missing")

def get_applications() -> list[dict[str, str, str]]:
    applications = []
    global app
    
    app_files = os.listdir()
    download_play_app = TMP_DOWNLOAD_PLAY_APP
    
    for file in app_files:
        if file.endswith("app.py"):
            applications.append({
                "file": file[:-3],
            })
            
    try:
        os.stat(download_play_app)  # Get file information
        applications.append({
            "file": download_play_app[:-3],
            "temporary": True
        })
    except OSError:
        pass
    
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


def gfx_expansion_modal(gfx, ctrl_name, attempts, success):
    mw = 199
    mh = 54
    cx = (gfx.dw-mw)//2
    cy = int((gfx.dh-mh)/2.5)
    padding = 6
    
    gfx.set_pen(display_config["theme"]["black"])
    gfx.rectangle(cx+padding, cy+padding, mw, mh)
    gfx.set_pen(display_config["theme"]["white"])
    gfx.rectangle(cx, cy, mw, mh)
    gfx.set_pen(display_config["theme"]["black"])
    gfx.text("Expansion installed", cx+padding, cy+7, scale=1)
    gfx.line(cx+3, cy+18, cx+mw-3, cy+18)
    
    gfx.set_pen(display_config["theme"]["grey"])
    ctrl_name_width = gfx.measure_text(ctrl_name, scale=1)
    gfx.text(ctrl_name, cx+mw-padding-ctrl_name_width, cy+7, scale=1)
    
    status = "Attemping to handshake..."
    if success == False:
        status = "Hankshake failure."
    if success == True:
        status = "Handshake success."
    gfx.text(status, cx+padding, cy+24)
    
    gspacing = 3
    gh = 14
    gw = (mw-padding*2-gspacing*4)//5
    gy = cy+35
    
    gfx.set_pen(display_config["theme"]["black"])
    for i in range(0, 5):
        gfx.rectangle(cx+padding+(i*(gw+gspacing)), gy, gw, gh)
        
    gfx.set_pen(display_config["theme"]["white"])
    
    for i in range(0, 5):
        gfx.rectangle(cx+padding+1+(i*(gw+gspacing)), gy+1, gw-2, gh-2)
        
    gfx.set_pen(display_config["theme"]["yellow"])
    if success==False:
        gfx.set_pen(display_config["theme"]["red"])
    for i in range(0, attempts):
        if i == attempts-1 and success:
            gfx.set_pen(display_config["theme"]["green"])
        gfx.rectangle(cx+padding+1+(i*(gw+gspacing)), gy+1, gw-2, gh-2)
            

def gfx_download_modal(gfx, ctrl_name, percent, success):
    mw = 199
    mh = 54
    cx = (gfx.dw-mw)//2
    cy = int((gfx.dh-mh)/2.5)
    padding = 6
    
    gfx.set_pen(display_config["theme"]["black"])
    gfx.rectangle(cx+padding, cy+padding, mw, mh)
    gfx.set_pen(display_config["theme"]["white"])
    gfx.rectangle(cx, cy, mw, mh)
    gfx.set_pen(display_config["theme"]["black"])
    gfx.text("Expansion App", cx+padding, cy+7, scale=1)
    gfx.line(cx+3, cy+18, cx+mw-3, cy+18)
    
    gfx.set_pen(display_config["theme"]["grey"])
    ctrl_name_width = gfx.measure_text(ctrl_name, scale=1)
    gfx.text(ctrl_name, cx+mw-padding-ctrl_name_width, cy+7, scale=1)
    
    status = "Attemping to sync app"
    gfx.text(status, cx+padding, cy+24)
    
    gfx.set_pen(display_config["theme"]["yellow"])
    
    if success:
        gfx.set_pen(display_config["theme"]["green"])
        
    gh = 14
    gy = cy+35
    gfx.rectangle(cx+padding, gy, int((mw-padding*2)*percent), gh)
    
    if success:
        gfx.set_pen(display_config["theme"]["white"])
        status = "App installed."
        gfx.text(status, cx+padding+padding, gy+5)