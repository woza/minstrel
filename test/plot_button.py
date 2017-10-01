#!/usr/bin/python

import buttons
import state_machine
import time
import RPi.GPIO as GPIO

inputs = buttons.group()

try:
    with open("button_state.dat", "w") as dest:
        inputs.liven()
        goal = inputs.gpio_button_map[state_machine.minstrel_state.ACTIONS.play]
        while True:
            now = time.time()
            bool_state = GPIO.input(goal)
            if bool_state:
                state = 1
            else:
                state = 0
            dest.write("%lf %d\n" % ( now, state ))
finally:
    print "Cleaning up"
    inputs.shutdown()
