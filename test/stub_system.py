class stub:
    def __init__(self, root):
        self.dirmap = {root:[]}
        self.state = 'stopped'
        
    def mkdir(self, containing_dir, name):
        self.dirmap[containing_dir] += [name]
        path = containing_dir + '/' + name
        self.dirmap[path] = []
        return path
                                        
    def add_file(self, containing_dir, name):
        self.dirmap[containing_dir] += [name]

    def query_play_state(self):
        return self.state

    def listdir(self, path):
        return self.dirmap[path]

    def isdir(self, path):
        return path in self.dirmap

    def launch_player(self, path):
        self.state = 'playing'

    def pause_player(self):
        self.state = 'paused'

    def stop_player(self):
        self.state = 'stopped'

    def rewind_player(self):
        pass

    def resume_player(self):
        self.state = 'playing'
