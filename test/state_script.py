#!/usr/bin/python

import state_machine
import stub_system
import inspect
import sys
import time

class failure:
    pass
def encode_state( machine, stub ):
    return "%s %s" % ( machine.query_current_selection(), stub.query_play_state())

def ensure( machine, stub, expect):
    called_from_line = inspect.stack()[1][2]
    actual = encode_state(machine, stub)
    msg = "[Line %d] - " % called_from_line
    if actual != expect:
        msg += "FAIL: Expected '%s' received '%s'" % ( expect, actual )
        print msg
        sys.exit(1)
    else:
        msg += "PASS"
        print msg
        
stub = stub_system.stub('root')
path = stub.mkdir('root', 'alpha_list')
stub.add_file(path, 'Alice')
stub.add_file(path, 'Adam')
stub.add_file(path, 'Anne')
stub.add_file(path, 'Alex')
p2 = stub.mkdir(path, 'angel_directory')
stub.add_file(p2, 'Anon')

path=stub.mkdir('root', 'beta_list')
stub.add_file(path, 'Bob')
stub.add_file(path, 'Belle')
stub.add_file(path, 'Brad')

stub.add_file('root', 'eve')

sm = state_machine.minstrel_state('root', stub)

##########################################
#   Navigation Tests
##########################################

# Ensure we cycle properly when moving forwards
ensure(sm, stub, 'alpha_list stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'beta_list stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'eve stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'alpha_list stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'beta_list stopped')

#Ensure we cycle properly when moving backwards
sm.process_input(sm.ACTIONS.backward)
ensure(sm, stub, 'alpha_list stopped')
sm.process_input(sm.ACTIONS.backward)
ensure(sm, stub, 'eve stopped')
sm.process_input(sm.ACTIONS.backward)
ensure(sm, stub, 'beta_list stopped')
sm.process_input(sm.ACTIONS.backward)
ensure(sm, stub, 'alpha_list stopped')
sm.process_input(sm.ACTIONS.backward)
ensure(sm, stub, 'eve stopped')

#Ensure we can enter and leave directories
sm.process_input(sm.ACTIONS.enter) # Entering a file is a no-op
ensure(sm, stub, 'eve stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'alpha_list stopped')
sm.process_input(sm.ACTIONS.enter)
ensure(sm, stub, 'Alice stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'Adam stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'Anne stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'Alex stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'angel_directory stopped')
sm.process_input(sm.ACTIONS.enter)
ensure(sm, stub, 'Anon stopped')
sm.process_input(sm.ACTIONS.leave)
ensure(sm, stub, 'angel_directory stopped')
sm.process_input(sm.ACTIONS.backward) #Ensure leave from a file works too
ensure(sm, stub, 'Alex stopped')
sm.process_input(sm.ACTIONS.leave)
ensure(sm, stub, 'alpha_list stopped')
sm.process_input(sm.ACTIONS.leave) # Leave at top level is no-op
ensure(sm, stub, 'alpha_list stopped')

##########################################
#   Playing/Pausing/Stopping Tests
##########################################

sm.process_input(sm.ACTIONS.play) # Play on directory is no-op
ensure(sm, stub, 'alpha_list stopped')
sm.process_input(sm.ACTIONS.enter)
ensure(sm, stub, 'Alice stopped')
sm.process_input(sm.ACTIONS.play)
ensure(sm, stub, 'Alice playing')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'Adam playing')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'Anne playing')
sm.process_input(sm.ACTIONS.backward) #Assumed within unrewind time
ensure(sm, stub, 'Adam playing')
delay = sm.query_rewind_trigger_delay() + 1
print "Pausing for %d seconds" % delay
time.sleep(delay)
sm.process_input(sm.ACTIONS.backward)
ensure(sm, stub, 'Adam playing') # Rewound
sm.process_input(sm.ACTIONS.backward) #Assumed within unrewind time
ensure(sm, stub, 'Alice playing')
sm.process_input(sm.ACTIONS.backward)
ensure(sm, stub, 'angel_directory stopped')
sm.process_input(sm.ACTIONS.forward)
ensure(sm, stub, 'Alice stopped')
sm.process_input(sm.ACTIONS.play)
ensure(sm, stub, 'Alice playing')
sm.process_input(sm.ACTIONS.play)
ensure(sm, stub, 'Alice paused')
sm.process_input(sm.ACTIONS.play)
ensure(sm, stub, 'Alice playing')
sm.process_input(sm.ACTIONS.play)
ensure(sm, stub, 'Alice paused')
sm.process_input(sm.ACTIONS.forward) # Moving off the paused track, should move to stopped
ensure(sm, stub, 'Adam stopped')
sm.process_input(sm.ACTIONS.play)
ensure(sm, stub, 'Adam playing')
sm.process_input(sm.ACTIONS.play)
ensure(sm, stub, 'Adam paused')
sm.process_input(sm.ACTIONS.backward)
ensure(sm, stub, 'Alice stopped')
sm.process_input(sm.ACTIONS.play)
ensure(sm, stub, 'Alice playing')
sm.process_input(sm.ACTIONS.play)
ensure(sm, stub, 'Alice paused')
sm.process_input(sm.ACTIONS.enter)
ensure(sm, stub, 'Alice paused')
sm.process_input(sm.ACTIONS.leave)
ensure(sm, stub, 'alpha_list stopped')

print "All Tests Passed"
