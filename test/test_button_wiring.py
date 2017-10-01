#!/usr/bin/python
import buttons
import state_machine
import time

debounce=0.1
inputs = buttons.group()
count=0
try:
    inputs.liven()
    while True:
        action = inputs.read_button_pressed()
        if action is not None:
            count += 1
            print "[%d] %s pressed" % (count, state_machine.minstrel_state.ACTIONS.name(action) )
#        time.sleep(debounce)

finally:
    print "Cleaning up"
    inputs.shutdown()
