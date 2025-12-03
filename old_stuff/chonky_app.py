'''
app["name"]="Chonky!!"
app["id"]="chonky_app"
app["icon"]="0000000000000000000100000000100000101000000101000010010000100100010001111110001001001100001100100101111111111010011111100111111001111111111111101111011111101111101101111110110111011110011110111011011001101101111110011001111101111111111111100001111111111000"
'''
import jpegdec
import slime_os as sos
from slime_os.libs.app_template import TemplateApp

class App(TemplateApp):
    def setup(self):
        self.display = display
        j = jpegdec.JPEG(self.display)
        self.display.set_pen(sos.config["theme"]["blue"])
        w, h = display.get_bounds()
        display.rectangle(0, 0, w, h)

        # Open the JPEG file
        j.open_file("chonky_bw.jpg")

        # Decode the JPEG, 50
        j.decode(39, 10, jpegdec.JPEG_SCALE_FULL)

    def run(self):
        yield sos.INTENT_FLIP_BUFFER
        while True:
            keys = sos.kbd.get_all()
            len_keys = len(keys)
            if len_keys:
                print(keys)
            if len_keys and keys[0] == 20:
                yield sos.INTENT_KILL_APP
                break
            yield sos.INTENT_NO_OP
        

if __name__ == '__main__':
    sos.boot(App)

