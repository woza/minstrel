#!/usr/bin/python

# Script that implements a version of the music player with two differences:
#   1. Renders to a TK image label instead of OLED screen
#   2. Input is via keyboard rather than buttons
#
# This allows testing of the core elements (system interface, models
# and view) on a laptop or other external debug machine.

import state_machine
import system
import minstrel
import tk_display
from Tkinter import *
import os
import sys

def make_screen( root ):
    screen = Label(root)
    screen.focus_set()
    screen.bind("f", dispatch_key_press )
    screen.bind("b", dispatch_key_press )
    screen.bind("e", dispatch_key_press )
    screen.bind("l", dispatch_key_press )
    screen.bind("p", dispatch_key_press )
    screen.bind("u", dispatch_key_press )
    screen.bind("d", dispatch_key_press )
    screen.pack()

    return screen

def dispatch_key_press( evt ):
    global model

    actions = state_machine.minstrel_state.ACTIONS
    if evt.char == 'f':
        model.process_input(actions.forward)
    if evt.char == 'b':
        model.process_input(actions.backward)
    if evt.char == 'e':
        model.process_input(actions.enter)
    if evt.char == 'l':
        model.process_input(actions.leave)
    if evt.char == 'p':
        model.process_input(actions.play)
    if evt.char == 'u':
        print "Dispatcing louder"
        model.process_input(actions.louder)
    if evt.char == 'd':
        print "Dispatching softer"
        model.process_input(actions.softer)

def heart_beat():
    global root, view, renderer

    view.refresh()
    renderer.display(view)

    root.after(100, heart_beat)


if len(sys.argv) < 2:
    print "Usage: %s <root directory of music collection>" % sys.argv[0]
    sys.exit(1)
        
root = Tk()
screen = make_screen(root)
ctrl = system.interface()
model = state_machine.minstrel_state( sys.argv[1], ctrl)
renderer = tk_display.renderer( screen )
view = minstrel.view(model, ctrl, renderer )

root.after(100, heart_beat)
root.mainloop()
