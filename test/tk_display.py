from Tkinter import *
from PIL import ImageTk

class renderer:
    def __init__(self, screen):
        self.screen = screen

    def screen_width_pixels(self):
        return 128

    def screen_height_pixels(self):
        return 32
    
    def display(self, view):
        output = ImageTk.PhotoImage(view.render())
        screen.cur_pic = output
        screen.configure(image=output)
