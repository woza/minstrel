#!/usr/bin/python

import sys
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class scrolling_window:
    def __init__(self, width):
        self.width = width
        self.text = ""
        # Blank spaces sufficient to fill the width
        self.padding = ''.join([' ' for i in range(width)])
        self.req_scrolling = False
        
    def set_text(self, text):
        if len(text) > self.width:
            self.req_scrolling = True
            self.text = text + self.padding
        else:
            self.req_scrolling = False
            self.text = text
        self.start = 0
        
    def query_snippet(self):
        if not self.req_scrolling:
            return self.text
        
        end = self.start + self.width
        if end > len(self.text):
            self.start = 0
            end = self.start + self.width
            
        snippet = self.text[self.start:self.start + self.width]
        self.start += 1
        return snippet

class view:
    def __init__( self, model, backend, dest):
        self.width = dest.screen_width_pixels()
        self.height = dest.screen_height_pixels()
        self.line_height=self.height/2
        self.backend = backend
        self.model = model
        self.image = Image.new('1', (self.width, self.height))
        self.draw_to = ImageDraw.Draw(self.image)
        self.font = ImageFont.load_default()

        self.system_line = scrolling_window(self.width)
        self.curr_line = scrolling_window(self.width)

    def refresh(self):
        self.curr_line.set_text(self.model.query_current_selection())
        temp = self.backend.query_temp()
        volume = self.backend.query_volume()
        status = "Temp: %s Vol: %d%%" % ( temp, volume )
        self.system_line.set_text(status)
        
    def clear_screen(self):
        self.draw_to.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        self.curr_line_row = 0
        
    def write_line(self, text):
        self.draw_to.text((0, self.curr_line_row), text, font=self.font, fill=255)
        self.curr_line_row += self.line_height
        
    def render(self):
        self.clear_screen()

        self.write_line( self.curr_line.query_snippet() )
        self.write_line( self.system_line.query_snippet() )
        
        return self.image
           
        
    
    
        

    
