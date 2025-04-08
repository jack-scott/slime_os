from machine import SoftI2C,Pin,UART,Timer,SPI
import time
from utils.drivers import KEYBOARD
from utils.drivers import SCREEN
from utils.fbconsole import FBConsole
import utils.color as color
import os
import st7789

NAME="jack but new"

screen=SCREEN(320,320)
kb=KEYBOARD()
time.sleep(1)

import machine, os
from machine import SPI,Pin

theme=color.COLOR_CANDY
scr = FBConsole(screen,bg_color=theme['bg'],fg_color=theme['font'])
os.dupterm(scr)

print('MPY CONSOLE ON PICOCALC by jd3096')
print('V1.02')
print('WELCOME! '+NAME)

for i in range(10):
    print(f"hello {i}\n")
    time.sleep(0.1)

# def check_key(t):
#     re=kb.check_key()
#     if re!=None:
#         if re[0]==3:
#             if re[1]==10:
#                 ip=b'\r\n'
#             else:
#                 ip=re[1].to_bytes(1,'big')
#             scr._c=ip
#             scr._press()

    
# tim=Timer(-1)
# tim.init(mode=Timer.PERIODIC, period=10, callback=check_key)




