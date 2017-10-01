import RPi.GPIO as GPIO
import state_machine
import time

class push_button:
    STATE_DOWN=0
    STATE_UP = 1
    
    def __init__(self, pin_num):
        self.pin = pin_num
        self.state = push_button.STATE_UP

    def state_changed(self):
        new_state = push_button.STATE_UP
        if GPIO.input(self.pin):
            new_state = push_button.STATE_DOWN
        if new_state == self.state:
            return False
        self.state = new_state
        return True

class group:
    def __init__(self):
        # BCM-numbered GPIO pin designators
        self.gpio_button_map={
            state_machine.minstrel_state.ACTIONS.louder : push_button(6),
            state_machine.minstrel_state.ACTIONS.softer : push_button(12),
            state_machine.minstrel_state.ACTIONS.enter : push_button(16),
            state_machine.minstrel_state.ACTIONS.forward : push_button(19),
            state_machine.minstrel_state.ACTIONS.leave : push_button(20),
            state_machine.minstrel_state.ACTIONS.play : push_button(21),
            state_machine.minstrel_state.ACTIONS.backward : push_button(26)
        }
        
    def liven(self):
        GPIO.setmode(GPIO.BCM)
        for label,button in self.gpio_button_map.iteritems():
            GPIO.setup( button.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN )

    def shutdown(self):
        GPIO.cleanup() # Reset all the pins we've used to a safe state

    def read_button_pressed( self ):
        for act, button in self.gpio_button_map.iteritems():
            toggled = button.state_changed()
            if toggled and button.state == push_button.STATE_DOWN:
                return act
        return None
    

