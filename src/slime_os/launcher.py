import time

from slime_os.keycode import Keycode
import os
import slime_os.system as sos

class HomeScreen:
    def setup(self, display):
        self.display = display

        self.do_get_apps()
        if not "launcher" in sos.persist:
            sos.persist["launcher"] = {
                "selected_app": 0
                }

        # display.set_gpu_io_adc_enable(29, True)
        time.sleep(0.002)

    def do_get_apps(self):
        self.apps = sos.get_applications()
        self.str_apps = str(self.apps)
                    

    def do_menu(self):
        gfx = sos.gfx
        if  sos.persist["launcher"]["selected_app"] < 0:
            sos.persist["launcher"]["selected_app"] = len(self.apps)-1
        if sos.persist["launcher"]["selected_app"] >= len(self.apps):
            sos.persist["launcher"]["selected_app"] = 0
            
        # print(sos.display_config["theme"])
        self.display.set_pen(*sos.display_config["theme"]["blue"])
        self.display.rectangle(0, 0, sos.gfx.dw, sos.gfx.dh)
        
        self.display.set_pen(*sos.display_config["theme"]["white"])
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
             
        
           self.display.set_pen(*sos.display_config["theme"]["white"])
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
  
               
           self.display.set_pen(*sos.display_config["theme"]["white"])
           
           name_width = self.display.measure_text(app["name"], scale=0.7)
           
           sos.gfx.text(app["name"], offset_x-1-(name_width//2), offset_y+14, scale=0.7)
                                             
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
            
    def run(self):
        last_selected_app = -1
        while True:
            if last_selected_app != sos.persist["launcher"]["selected_app"]:
                self.do_menu()
                yield sos.INTENT_FLIP_BUFFER
                last_selected_app = sos.persist["launcher"]["selected_app"]
                
            keys = sos.kbd.get_keys([
                Keycode.ENTER,
                Keycode.LEFT_ARROW,
                Keycode.RIGHT_ARROW
            ])
            
            if keys[Keycode.LEFT_ARROW]:
                sos.persist["launcher"]["selected_app"] -= 1
            if keys[Keycode.RIGHT_ARROW]:
                sos.persist["launcher"]["selected_app"] += 1
            if keys[Keycode.ENTER]:
                yield sos.INTENT_REPLACE_APP(
                    self.apps[sos.persist["launcher"]["selected_app"]]
                    )
                break
            
            yield sos.INTENT_NO_OP
            
        
    def cleanup(self):
        pass

    
if __name__ == '__main__':
    __import__("slime_os").boot(App)