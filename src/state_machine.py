#!/usr/bin/python

import sys
import os
from minstrel_enum import enum_type
import misc
import time

class minstrel_logic_error (Exception):
    pass

class area:
    def __init__(self, path, system):
        self.system = system
        self.path = path
        self.contents = system.listdir(path)
        self.idx = -1
        self.step(1)

    def step(self, inc):
        if len(self.contents) == 0:
            self.idx = 0
            self.curr_path = None
            return
        self.idx = (self.idx + inc) % len(self.contents)
        self.curr_path = self.contents[ self.idx ]
        self.full_path = os.path.join(self.path, self.curr_path)
        self.kind='song'
        if self.system.isdir(self.full_path):
            self.kind='group'

class minstrel_state:
    STATES = enum_type(['halted', 'started', 'playing', 'paused', 'stepping', 'start_paused'])
    SELECTABLE=enum_type(['file', 'directory'])
    ACTIONS=enum_type(['forward', 'backward', 'enter', 'leave', 'play', 'louder', 'softer',
                       'auto', 'elapsed'])
    ANY=None
    def __init__( self, root, system):
        self.root_dir = root
        self.area_stack = [area(root, system)]
        self.system_handle = system
        
        state = minstrel_state.STATES
        obj = minstrel_state.SELECTABLE
        act = minstrel_state.ACTIONS
        any = minstrel_state.ANY
        stop_and_enter=[self.terminate, self.enter_dir]
        stop_and_up=[self.terminate, self.up_dir]
        stop_and_next = [self.terminate, self.next]
        stop_and_prev = [self.terminate, self.prev]
        
        self.state_table = [
            [(state.halted, any), act.forward, (state.halted, self.next)],
            [(state.halted, any), act.backward, (state.halted, self.prev)],
            [(state.halted, any), act.leave, (state.halted, self.up_dir)],
            [(state.halted, obj.file), act.enter, (state.halted, self.no_op)],
            [(state.halted, obj.directory), act.enter, (state.halted, self.enter_dir)],
            [(state.halted, obj.file), act.play, (state.started, self.launch)],
            [(state.halted, obj.directory), act.play, (state.halted, self.no_op)],
            [(state.halted, any), act.elapsed, (state.halted, self.impossible)],
            [(state.halted, any), act.auto, (state.halted, self.impossible)],
            [(state.halted, any), act.louder, (state.halted, self.no_op)],
            [(state.halted, any), act.softer, (state.halted, self.no_op)],
            
            [(state.started, obj.file), act.forward, (state.started, self.started_next)],
            [(state.started, obj.file), act.backward, (state.started, self.started_prev)],
            [(state.started, obj.file), act.enter, (state.started, self.no_op)],
            [(state.started, obj.file), act.leave, (state.halted, stop_and_up)],
            [(state.started, obj.file), act.play, (state.start_paused, self.pause)],
            [(state.started, obj.file), act.auto, (state.halted, self.impossible)],
            [(state.started, obj.file), act.elapsed, (state.playing, self.no_op)],
            [(state.started, obj.directory), any, (state.halted, self.impossible)],
            [(state.started, any), act.louder, (state.started, self.louder)],
            [(state.started, any), act.softer, (state.started, self.softer)],
            
            [(state.playing, obj.file), act.forward, (state.started, self.playing_next)],
            [(state.playing, obj.file), act.backward, (state.started, self.rewind)],
            [(state.playing, obj.file), act.enter, (state.started, self.no_op)],
            [(state.playing, obj.file), act.leave, (state.halted, stop_and_up)],
            [(state.playing, obj.file), act.play, (state.paused, self.pause)],
            [(state.playing, obj.file), act.auto, (state.halted, self.impossible)],
            [(state.playing, obj.file), act.elapsed, (state.halted, self.impossible)],
            [(state.playing, obj.directory), any, (state.halted, self.impossible)],
            [(state.playing, any), act.louder, (state.playing, self.louder)],
            [(state.playing, any), act.softer, (state.playing, self.softer)],

            [(state.paused, obj.file), act.forward, (state.halted, stop_and_next)],
            [(state.paused, obj.file), act.backward, (state.halted, stop_and_prev)],
            [(state.paused, obj.file), act.enter, (state.paused, self.no_op)],
            [(state.paused, obj.file), act.leave, (state.halted, stop_and_up)],
            [(state.paused, obj.file), act.play, (state.playing, self.resume)],
            [(state.paused, obj.file), act.auto, (state.halted, self.impossible)],
            [(state.paused, obj.file), act.elapsed, (state.halted, self.impossible)],
            [(state.paused, obj.directory), any, (state.halted, self.impossible)],
            [(state.paused, any), act.louder, (state.paused, self.louder)],
            [(state.paused, any), act.softer, (state.paused, self.softer)],

            [(state.start_paused, obj.file), act.forward, (state.halted, stop_and_next)],
            [(state.start_paused, obj.file), act.backward, (state.halted, stop_and_prev)],
            [(state.start_paused, obj.file), act.enter, (state.start_paused, self.no_op)],
            [(state.start_paused, obj.file), act.leave, (state.halted, stop_and_up)],
            [(state.start_paused, obj.file), act.play, (state.started, self.resume)],
            [(state.start_paused, obj.file), act.auto, (state.halted, self.impossible)],
            [(state.start_paused, obj.file), act.elapsed, (state.halted, self.impossible)], #???
            [(state.start_paused, obj.directory), any, (state.halted, self.impossible)],
            [(state.start_paused, any), act.louder, (state.start_paused, self.louder)],
            [(state.start_paused, any), act.softer, (state.start_paused, self.softer)],

        ]        
        self.curr_state = state.halted
        self.rewind_until_sec = 5
        self.pending_transition = None
        
        
    def query_rewind_trigger_delay(self):
        return self.rewind_until_sec

    def selected_kind(self):
        if self.area_stack[-1].kind == 'group':
            return minstrel_state.SELECTABLE.directory
        return minstrel_state.SELECTABLE.file

    def process_input(self, action):
        if self.pending_transition is not None:
            if time.time() >= self.pending_transition[0]:
                lazy_input = self.pending_transition[1]
                self.pending_transition = None
                self.process_input( lazy_input )
                
        selected=self.selected_kind()

        entry = self.lookup(self.curr_state, selected, action)
        self.pending_next_state, raw_handlers = entry[2]
        handlers = misc.ensure_array(raw_handlers)
        print "Looked up %s handlers %s" %(self.entry_key_to_string(entry), self.handlers_to_string(handlers))

        for h in handlers:
            h(entry) # Might modify pending_next_state

        self.curr_state = self.pending_next_state

    def validate_state_table(self):
        for state in minstrel_state.STATES:
            for selected in minstrel_state.SELECTABLE:
                for action in minstrel_state.ACTIONS:
                    ignored = self.lookup(state, selected, action)

    def handlers_to_string(self, handlers):
        return '->'.join([f.func_name for f in handlers])
    
    def entry_key_to_string(self, entry):
        state_name = 'ANY'
        select_name = 'ANY'
        action_name = 'ANY'
        if entry[0][0] is not minstrel_state.ANY:
            state_name=minstrel_state.STATES.name(entry[0][0])
        if entry[0][1] is not minstrel_state.ANY:
            select_name=minstrel_state.SELECTABLE.name(entry[0][1])
        if entry[1] is not minstrel_state.ANY:
            action_name=minstrel_state.ACTIONS.name(entry[1])
            
        return "state %s, selected %s, action %s" % (state_name, select_name, action_name)
    
    def lookup(self, state, selected, action):
        # To do: more efficient lookup iff this is a bottleneck
        res=[]
        for entry in self.state_table:
            if entry[0][0] == state or entry[0][0] == minstrel_state.ANY:
                if entry[0][1] == selected or entry[0][1] == minstrel_state.ANY:
                    if entry[1] == action or entry[1] == minstrel_state.ANY:
                        res += [entry]

        if len(res) != 1:
            msg = "Invalid number of results (%d) retrieved " \
                  "for state %s, selected %s, action %s" % ( len(res), state, selected, action)
            raise minstrel_state_logic_error(msg)
        return res[0]

    def launch(self, entry):
        self.system_handle.launch_player(self.area_stack[-1].full_path)
        self.pending_transition = (time.time() + self.query_rewind_trigger_delay(),
                                   minstrel_state.ACTIONS.elapsed)
        
    def pause(self, entry):
        self.system_handle.pause_player()
        # Don't update pending_transition
        
    def terminate(self, entry):
        self.system_handle.stop_player()
        self.pending_transition = None
        
    def rewind(self, entry):
        self.system_handle.rewind_player()
        self.pending_transition = (time.time() + self.query_rewind_trigger_delay(),
                                   minstrel_state.ACTIONS.elapsed)

    def resume(self, entry):
        self.system_handle.resume_player()
        # Don't update pending_transition
        
    def impossible(self, entry):
        raise minstrel_logic_error("Impossible state achieved: " + self.entry_key_to_string(entry))

    def no_op(self, entry):
        pass

    def next(self, entry):
        self.area_stack[-1].step(1)

    def prev(self, entry):
        self.area_stack[-1].step(-1)

    def up_dir(self, entry):
        if len(self.area_stack) > 1:
            self.area_stack = self.area_stack[:-1]
        
    def enter_dir(self, entry):
        top = self.area_stack[-1]
        new_dir=os.path.join(top.path, top.curr_path)
        self.area_stack += [ area(new_dir, self.system_handle) ]

    def louder(self, entry):
        print "Increasing volume"
        self.system_handle.increase_volume()

    def softer(self, entry):
        print "Reducing volume"
        self.system_handle.decrease_volume()

    def started_next(self, entry):
        self.navigate_while_activated(entry, self.next)

    def started_prev(self, entry):
        self.navigate_while_activated(entry, self.prev)

    def playing_next(self, entry):
        self.navigate_while_activated(entry, self.next)

    def navigate_while_activated( self, entry, step_func ):
        self.terminate(entry)
        step_func( entry )
        if self.selected_kind() == minstrel_state.SELECTABLE.directory:
            self.pending_next_state =  minstrel_state.STATES.halted
        else:
            self.launch(entry)
            
    def query_current_selection(self):
        return self.area_stack[-1].curr_path
