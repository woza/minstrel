import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

class renderer:
    def __init__(self):
        self.screen  = Adafruit_SSD1306.SSD1306_128_32(rst=None)
        self.screen.begin()
        self.screen.clear()
        self.screen.display()

    def screen_width_pixels(self):
        return self.screen.width

    def screen_height_pixels(self):
        return self.screen.height
    
    def display(self, view):
        image = view.render()
        self.screen.clear()
        self.screen.image(image)
        self.screen.display()
