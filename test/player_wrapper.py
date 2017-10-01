#!/usr/bin/python

# Script that wraps the system player, to enable simple manual checking of the control interface.

import system
import os
import sys
import termios
import tty


if len(sys.argv) < 2:
    print "Usage: %s <path of music file>" % sys.argv[0]
    sys.exit(1)

ctrl = system.interface()
restore_attr = termios.tcgetattr(sys.stdin)
new_attr = termios.tcgetattr(sys.stdin)
new_attr[3] = new_attr[3] & ~termios.ECHO    
tty.setraw(sys.stdin)
try:
    termios.tcsetattr(sys.stdin, termios.TCSANOW,new_attr)
    while True:
        c = sys.stdin.read(1)
        if c == 'q':
            break
        if c == 'p':
            print "Pausing"
            ctrl.pause_player()
        if c == 'r':
            print "Resuming"
            ctrl.resume_player()
        if c == 'l':
            print "Launching"
            ctrl.launch_player(sys.argv[1])
        if c == 's':
            print "Stopping"
            ctrl.stop_player()
        if c == 'b':
            print "Rewinding"
            ctrl.rewind_player()
        if c == 'u':
            print "Vol up"
            ctrl.increase_volume()
        if c == 'd':
            print "Vol down"
            ctrl.decrease_volume()
        if c == 'h':
            msg="""
Commands:
q - quit
p - pause
r - resume
l - launch
s - stop
b - rewind
u - increase volume
d - decrease volume
"""
            print msg
            
finally:
    termios.tcsetattr(sys.stdin, termios.TCSANOW, restore_attr)
    
