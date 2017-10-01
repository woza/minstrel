#!/usr/bin/python

import state_machine
import system
import minstrel
import oled
import time
import buttons


debounce_seconds=0.1
press_window=0.5
ctrl = system.interface()
model = state_machine.minstrel_state('/opt/music', ctrl)
renderer = oled.renderer()
view = minstrel.view(model, ctrl, renderer)


try:
    inputs = buttons.group()
    inputs.liven()
    while True:
        action = inputs.read_button_pressed()
        if action is not None:
            print "Received action %s" % state_machine.minstrel_state.ACTIONS.name(action)
            model.process_input(action)
            view.refresh()
            renderer.display(view)        
            time.sleep(press_window)
        else:
            view.refresh()
            renderer.display(view)        
            time.sleep(debounce_seconds)
finally:
    print "Cleaning up"
    inputs.shutdown()

