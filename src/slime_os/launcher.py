import gc
import time
import math
import random
from machine import ADC
import os
from picovision import PicoVision, PEN_P5
from pimoroni import Button
import slime_os as sos

from machine import Pin, I2C, UART, SPI

import sdcard

from slime_os.graphics import *
from slime_os.expansion import *

import slime_os.intents as intents
from slime_os.intents import *

from slime_os.keycode import Keycode as keycode

from slime_os.keyboard import Keyboard

from slime_os.device_config import my_device

TMP_DOWNLOAD_PLAY_APP = "/sd/download_play_app.py"

def get_internal_i2c():
    return I2C(1, scl=Pin(my_device.KEYBOARD_SCL), sda=Pin(my_device.KEYBOARD_SDA))

def get_expansion_i2c():
    return I2C(1, scl=Pin(my_device.EXPANSION_SCL), sda=Pin(my_device.EXPANSION_SDA))

def get_expansion_uart(baudrate=115200):
    return UART(0, baudrate, tx=Pin(my_device.EXPANSION_UART_TX), rx=Pin(my_device.EXPANSION_UART_RX))
    
def get_sdcard():
    sd_spi = SPI(1, sck=Pin(my_device.SD_CARD_SCK, Pin.OUT), mosi=Pin(my_device.SD_CARD_MOSI, Pin.OUT), miso=Pin(my_device.SD_CARD_MISO, Pin.OUT))
    return sdcard.SDCard(sd_spi, Pin(my_device.SD_CARD_CS))

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


# display = PicoVision(PEN_P5, 400, 240)
gfx = Gfx(display)
ctrl = Ctrl(display)
kbd = Keyboard(my_device.KEYBOARD_DRIVER)

sd = get_sdcard()
persist = {}
os.mount(sd, "/sd")
try:
    os.remove(TMP_DOWNLOAD_PLAY_APP)
    print("[sos].temp_file_removed")
except:
    print("[sos].temp_file_missing")
    
def boot(next_app):

    for key,color in config["theme"].items():
        if isinstance(color, tuple):
            config["theme"][key] = display.create_pen(*color)
            
    running_app = next_app()
    running_app_instance = None

    while True:
        if running_app:
            if not running_app_instance:
                running_app.setup(display)
                running_app_instance = running_app.run()
            intent = next(running_app_instance)
        else:
            intent = INTENT_FLIP_BUFFER
            
        if is_intent(intent, INTENT_KILL_APP):
            running_app = None
            running_app_instance = None
            print("[SOS].APP_KILLED")
            gc.collect()
            
            next_app = launcher.App
            if len(intent) == 2:
                next_app = __import__(intent[1]["file"]).App
            running_app = next_app()
            
        if is_intent(intent, INTENT_NO_OP):
            pass
        
        
        if is_intent(intent, INTENT_FLIP_BUFFER):
            display.set_pen(config["theme"]["black"])
            display.rectangle(0, 0, gfx.dw, 40)
            display.set_pen(config["theme"]["white"])
            display.line(gfx.dw-12, 40, gfx.dw-12-120, 40)
            display.line(0+12, 40, 0+12+120, 40)
            
            window_title = "SLIMEDECK ZERO"
            
            display.text(window_title, gfx.dw-12-10, 31, -1, 1, 180)
            display.text(free(), 0+12+86, 31, -1, 1, 180)
            display.update()

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
        
        gfx.set_pen(sos.config["theme"]["black"])
        gfx.rectangle(cx+padding, cy+padding, mw, mh)
        gfx.set_pen(sos.config["theme"]["white"])
        gfx.rectangle(cx, cy, mw, mh)
        gfx.set_pen(sos.config["theme"]["black"])
        gfx.text("Expansion installed", cx+padding, cy+7, scale=1)
        gfx.line(cx+3, cy+18, cx+mw-3, cy+18)
        
        gfx.set_pen(sos.config["theme"]["grey"])
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
        
        gfx.set_pen(sos.config["theme"]["black"])
        for i in range(0, 5):
            gfx.rectangle(cx+padding+(i*(gw+gspacing)), gy, gw, gh)
            
        gfx.set_pen(sos.config["theme"]["white"])
        
        for i in range(0, 5):
            gfx.rectangle(cx+padding+1+(i*(gw+gspacing)), gy+1, gw-2, gh-2)
            
        gfx.set_pen(sos.config["theme"]["yellow"])
        if success==False:
            gfx.set_pen(sos.config["theme"]["red"])
        for i in range(0, attempts):
            if i == attempts-1 and success:
                gfx.set_pen(sos.config["theme"]["green"])
            gfx.rectangle(cx+padding+1+(i*(gw+gspacing)), gy+1, gw-2, gh-2)
            

def gfx_download_modal(gfx, ctrl_name, percent, success):
        mw = 199
        mh = 54
        cx = (gfx.dw-mw)//2
        cy = int((gfx.dh-mh)/2.5)
        padding = 6
        
        gfx.set_pen(sos.config["theme"]["black"])
        gfx.rectangle(cx+padding, cy+padding, mw, mh)
        gfx.set_pen(sos.config["theme"]["white"])
        gfx.rectangle(cx, cy, mw, mh)
        gfx.set_pen(sos.config["theme"]["black"])
        gfx.text("Expansion App", cx+padding, cy+7, scale=1)
        gfx.line(cx+3, cy+18, cx+mw-3, cy+18)
        
        gfx.set_pen(sos.config["theme"]["grey"])
        ctrl_name_width = gfx.measure_text(ctrl_name, scale=1)
        gfx.text(ctrl_name, cx+mw-padding-ctrl_name_width, cy+7, scale=1)
        
        status = "Attemping to sync app"
        gfx.text(status, cx+padding, cy+24)
        
        gfx.set_pen(sos.config["theme"]["yellow"])
        
        if success:
            gfx.set_pen(sos.config["theme"]["green"])
            
        gh = 14
        gy = cy+35
        gfx.rectangle(cx+padding, gy, int((mw-padding*2)*percent), gh)
        
        if success:
            gfx.set_pen(sos.config["theme"]["white"])
            status = "App installed."
            gfx.text(status, cx+padding+padding, gy+5)


class App:
    def setup(self, display):
        self.display = display

        self.do_get_apps()
        if not "launcher" in sos.persist:
            sos.persist["launcher"] = {
                "selected_app": 0
                }

        display.set_gpu_io_adc_enable(29, True)
        time.sleep(0.002)

    def do_get_apps(self):
        self.apps = sos.get_applications()
        self.str_apps = str(self.apps)
        
    def do_uart_expansion(self):
        ctrl = sos.ctrl
        gfx = sos.gfx
        ctrl_value = ctrl.get()
        
        uart = sos.get_expansion_uart()
        
        accepted = False
        for i in range(0, 6):
            time.sleep(1)
            print(f"[EXP].HANDSHAKE_WAITING: {i}")
            if i != 5:
                gfx_expansion_modal(sos.gfx, sos.CTRL_NAMES[ctrl_value], i, None)
                yield sos.INTENT_FLIP_BUFFER
            uart_data = uart.readline()
            
            if uart_data:
                data_string = ''.join([chr(b) for b in uart_data])
                print(f"> {data_string}")
                if data_string.strip()[0:5] == "[sos]":
                    print("[EXP].HANDSHAKE_ACCEPTED")
                    accepted = True
                    gfx_expansion_modal(gfx, sos.CTRL_NAMES[ctrl_value], i, True)
                    yield sos.INTENT_FLIP_BUFFER
                    break
            else:
                print("> [no data]")
                
        if not accepted:
            gfx_expansion_modal(gfx, sos.CTRL_NAMES[ctrl_value], i, False)
            yield sos.INTENT_FLIP_BUFFER
            print("[EXP].HANDSHAKE_REJECTED")
                    

    def do_menu(self):
        gfx = sos.gfx
        if  sos.persist["launcher"]["selected_app"] < 0:
            sos.persist["launcher"]["selected_app"] = len(self.apps)-1
        if sos.persist["launcher"]["selected_app"] >= len(self.apps):
            sos.persist["launcher"]["selected_app"] = 0
            
        self.display.set_pen(sos.config["theme"]["blue"])
        self.display.rectangle(0, 0, sos.gfx.dw, sos.gfx.dh)
        
        self.display.set_pen(sos.config["theme"]["white"])
        for app_index, app in enumerate(self.apps):

           offset_x = 50 + (app_index * 64)
           offset_y = 32
           
           is_temporary = "temporary" in app and app["temporary"] == True
           is_selected = app_index == sos.persist["launcher"]["selected_app"]
           show_outline = is_selected
           
           if show_outline:
               sos.gfx.line(offset_x+31, offset_y+28, offset_x-32, offset_y+28,3)
               sos.gfx.line(offset_x+31, offset_y-14, offset_x-31, offset_y-14)
               sos.gfx.line(offset_x+31, offset_y+28, offset_x+31, offset_y-15)
               sos.gfx.line(offset_x-31, offset_y+28, offset_x-31, offset_y-15)
             
        
           self.display.set_pen(sos.config["theme"]["white"])
           if is_temporary:
               for i in range(-2, 4):
                   dx = (i*6) - 6
                   sos.gfx.line(offset_x+dx, offset_y+23, offset_x+dx+4, offset_y+23, 2)
               
           '''if is_temporary and not is_selected:
               
               for i in range(-2, 4):
                   dy = 4+i*7
                   sos.gfx.line(offset_x+34, offset_y+dy, offset_x-35, offset_y+dy, 3)
               for i in range(-4, 4):
                   dx = 4+i*8
                   sos.gfx.line(offset_x+dx, offset_y-16, offset_x+dx, offset_y+30, 3)
               #sos.gfx.line(offset_x-32, offset_y+28, offset_x-32, offset_y-15, 5)'''
  
               
           self.display.set_pen(sos.config["theme"]["white"])
           
           name_width = self.display.measure_text(app["name"], scale=1)
           
           sos.gfx.text(app["name"], offset_x-1-(name_width//2), offset_y+14)
                                             
           if "icon" in app:
               size = -1
               if len(app["icon"]) == 256:
                   size = 16
               else:
                   print("Unknown icon length for {0} of {1}".format(app['name'], len(app["icon"])))
                   
               if size != -1:
                   for bit_index, bit in enumerate(app["icon"]):
                       if bit == "1":
                           y = (bit_index // size) - size//2
                           x = (bit_index % size) - size//2
                           sos.gfx.pixel(offset_x + x, offset_y  + y)

    def do_download_play(self):
        uart = sos.get_expansion_uart()
        uart.write(bytes("[sos].app", "ascii"))
        time.sleep(0.1)
        
        fails = 0
        line = ''
        length = 1
        size = 0
        
        tmp_file = "/sd/download_play_app.py"
        with open(tmp_file, "w") as f:
            while True:
                uart_data = uart.read(128)
                
                if uart_data is not None:
                    fails = 0
                    for b in uart_data:
                        char = chr(b)
                        line += char
                        
                        if char == "\n":
                            
                            if line[0:14] == "[sos].app:yes:":
                                size = int(line[14:])
                                print("[EXP].APP_DOWNLOAD_START")
                                yield (-size + length)
                            elif line[0:14] == "[\sos].app:yes":
                                yield (-size + length)
                                print(f"[EXP].APP_DOWNLOAD_END:{length} of {size}")
                                break
                            else:
                                length += len(line)
                                f.write(line)
                                yield (-size + length)
                            line = ""
                            
                else:
                    fails += 1
                    if (fails > 10000):
                        break
                    
            f.close()
            
    def run(self):
        last_selected_app = -1
        while True:
            if sos.ctrl.check():
                ctrl_value = sos.ctrl.get()
                ctrl_name = sos.CTRL_NAMES[ctrl_value]
                print(f"[EXP].CHANGE: {ctrl_name}")
                if ctrl_value == sos.CTRL_EMPTY:
                    try:
                        os.remove("/sd/download_play_app.py")
                        print("[sos].temp_file_removed")
                    except:
                        print("[sos].temp_file_missing")
                
                if ctrl_value == sos.CTRL_UART_115200:
                    do = self.do_uart_expansion()
                    last_selected_app = sos.persist["launcher"]["selected_app"]
                    
                    while do:
                        self.do_menu()
                        try:
                            yield next(do)
                        except StopIteration:
                            time.sleep(3)
                            break
                        
                    do = self.do_download_play()
                    size = -next(do)
                    while do:
                        try:
                            remaining = next(do)
                            percent = 1-(-remaining/size)
                            gfx_download_modal(sos.gfx, ctrl_name, percent, remaining == 0)
                            yield sos.INTENT_FLIP_BUFFER
                        except StopIteration:
                            time.sleep(3)
                            break
                    
                self.do_get_apps()
                self.do_menu()
                yield sos.INTENT_FLIP_BUFFER
            
            if last_selected_app != sos.persist["launcher"]["selected_app"]:
                self.do_menu()
                yield sos.INTENT_FLIP_BUFFER
                last_selected_app = sos.persist["launcher"]["selected_app"]
                
            keys = sos.kbd.get_keys([
                sos.keycode.ENTER,
                sos.keycode.LEFT_ARROW,
                sos.keycode.RIGHT_ARROW
            ])
            
            if keys[sos.keycode.LEFT_ARROW]:
                sos.persist["launcher"]["selected_app"] -= 1
            if keys[sos.keycode.RIGHT_ARROW]:
                sos.persist["launcher"]["selected_app"] += 1
            if keys[sos.keycode.ENTER]:
                yield sos.INTENT_REPLACE_APP(
                    self.apps[sos.persist["launcher"]["selected_app"]]
                    )
                break
            
            yield sos.INTENT_NO_OP
            
        
    def cleanup(self):
        pass

    
if __name__ == '__main__':
    __import__("slime_os").boot(App)