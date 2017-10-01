import os
import subprocess
import threading
import thermometer
import errno

# class volume_monitor(threading.Thread):

#     def __init__(self, fd):
#         threading.Thread.__init__()
#         self.source_fd = fd
#         self.mutex = threading.Lock()
#         self.value = '???'

#     def run(self):
#         consuming = False
#         memory = "xxxxx"
#         while True:
#             c = os.read(self.source_fd, 1)
#             if not consuming:
#                 memory = memory[1:] + c
#                 if memory == "Vol: ":
#                     consuming = True
#                     num_text=''
#             else:
#                 if c == '(':
#                     consuming = False
#                     memory = "xxxxx"
#                     self.mutex.acquire()
#                     self.value = num_text
#                     self.mutex.release()
#                 else:
#                     num_text += c

class interface:
    def __init__(self):
        self.state = 'stopped'
        self.handle = None
        self.monitor_thread = None
        self.temp_save_file = '/var/minstrel/state.temp'
        self.temp_sensor = thermometer.fetch()
        self.init_volume()
        
    def init_volume(self):
        self.volume_step = 1
        self.volume_save_file = '/var/minstrel/state/volume'

        tmp = self.load_from_file(self.volume_save_file)
        if tmp is None:
            self.persistent_volume = 100
        else:
            self.persistent_volume = int(tmp)
            if self.persistent_volume < 0:
                self.persistent_volume = 0
            if self.persistent_volume > 100:
                self.persistent_volume = 100

    def save_to_file(self, dest_path, value):
        # Two step save to reduce the chance of data corruption if
        # battery fails / power plug pulled
        with open(self.temp_save_file, 'w') as dest:
            dest.write(value)
        # Atomic rename
        os.rename( self.temp_save_file, dest_path )

    def load_from_file(self, src_path):
        try:
            with open(src_path) as src:
                return src.read()
        except IOError as e:
            if e.errno == errno.ENOENT:
                return None
            raise e
            
    def query_temp(self):
        return self.temp_sensor.read_degrees_centigrade()

    def query_volume(self):
        return self.persistent_volume

    def query_play_state(self):
        return self.state

    def listdir(self, path):
        return os.listdir(path)

    def isdir(self, path):
        return os.path.isdir(path)

    def launch_player(self, path):
        self.tty_out, self.child_in = os.openpty()
        sink = open('/tmp/mplay.out', 'w')
        print "Launching '%s'" % path
        self.handle = subprocess.Popen(['/usr/bin/mpg123', "-v", "-C", path],
                                       shell=False,
                                       stdout=sink,
                                       stderr=subprocess.STDOUT,
                                       stdin=self.child_in)
        self.set_initial_volume()
        self.state = 'playing'

    def pause_player(self):
        if self.handle is not None:
            os.write(self.tty_out, 's')
            self.state = 'paused'

    def stop_player(self):
        if self.handle is not None:
            self.handle.terminate()
            self.handle = None
        self.state = 'stopped'

    def rewind_player(self):
        if self.handle is not None:
            os.write(self.tty_out, 'b')

    def resume_player(self):
        if self.handle is not None and self.state == 'paused':
            os.write(self.tty_out, 's')
            self.state = 'playing'

    def increase_volume(self):
        max_volume = 100
        delta = min(self.volume_step, max_volume - self.persistent_volume)
        self.adjust_volume(delta, '+')

    def decrease_volume(self):
        delta = min(self.volume_step, self.persistent_volume)
        self.adjust_volume( -delta, '-' )

    def adjust_volume(self, delta, cmd):
        if delta != 0:
            self.persistent_volume += delta
            count = delta
            if count < 0:
                count = -delta
            if self.handle is not None:
                cmd = ''.join([cmd for i in range(count)])
                print "Writing '%s'" % cmd
                os.write(self.tty_out, cmd)
            self.save_to_file( self.volume_save_file, str(self.persistent_volume) )

    def set_initial_volume(self):
        num_decrement_ops = 100 - self.persistent_volume
        decrement_cmd = ''.join(['-' for i in range(num_decrement_ops)])
        os.write(self.tty_out, decrement_cmd)
