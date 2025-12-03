from slime_os.device_config import my_device
from config import config as display_config

class Gfx:
    def __init__(self, instance:str = None):
        if instance is None:
            instance = my_device.DISPLAY_DRIVER
        if instance == "pico_calc":
            from slime_os.drivers.display.pico_calc_display import PicoCalcDisplay
            self.display = PicoCalcDisplay()
        elif instance == "picovision":
            from slime_os.drivers.display.picovision import PicovisionDisplay
            self.display = PicovisionDisplay()
        else:
            raise ValueError("Invalid display instance")
    
        self.dw, self.dh = self.display.get_bounds()

        self.is_flipped = display_config["display"]["flipped"]
    
    def set_pen(self, r, g, b):
        self.display.set_pen(r, g, b)
        

    def get_bounds(self):     
        return self.display.get_bounds()
 
    def _adjust_x(self, x, w=0):
        if self.is_flipped:
            return int(self.dw - w - x)
        else:
            return int(x)
        
    def _adjust_y(self, y, h=0):
        if self.is_flipped:
            return int(self.dh - h - y)
        else:
            return int(y)
        
    def rectangle(self, x, y, w, h):
        x = self._adjust_x(x, w)
        y = self._adjust_y(y, h)
        self.display.rectangle(x,y,w,h)
        
    def pixel(self, x, y):
        x = self._adjust_x(x)
        y = self._adjust_y(y)
        self.display.pixel(x,y)
        
    def line(self, x1, y1, x2, y2, t=1):
        x1 = self._adjust_x(x1)
        y1 = self._adjust_y(y1)
        x2 = self._adjust_x(x2)
        y2 = self._adjust_y(y2)
        self.display.line(x1,y1,x2,y2,t)
        
    def text(self, text, x, y, scale=1, angle=0):
        x = self._adjust_x(x)
        y = self._adjust_y(y)
        
        if self.is_flipped:
            angle = 180
            x -= scale
            y -= 0
        self.display.text(text, x,y, scale, angle)
    
    def measure_text(self, text, scale=1):
        return self.display.measure_text(text, scale)
    
    def update(self):
        return self.display.update()
    
if __name__ == "__main__":
    import time
    gfx = Gfx()
    gfx.set_pen(255, 0, 0)
    x1 = 0
    y1 = 0
    x2 = 1
    y2 = 1
    for i in range(1, 319):
        x2 = i
        y2 = i
        gfx.rectangle(x1, y1, x2, y2)
        time.sleep(0.01)
        gfx.update()

    gfx.rectangle(10, 10, 100, 50)
    gfx.set_pen(0, 255, 0)
    gfx.pixel(20, 20)
    gfx.set_pen(0, 0, 255)
    gfx.line(30, 30, 80, 80)
    gfx.set_pen(255, 255, 0)
    gfx.text("Hello World", 40, 40)
    gfx.update()