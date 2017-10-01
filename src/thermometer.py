import os.path
import glob

class linux_thermal_zone:
    def __init__(self, goal_type):
        matches = []
        zones = [ os.path.basename(x) for x in glob.glob('/sys/class/thermal/thermal_zone*') ]
        for zone_name in zones:
            with open('/sys/class/thermal/%s/type' % zone_name) as src:
                kind = src.read().strip()
            if kind == goal_type:
                matches += [zone_name]

        print "Matches = " + str(matches)
        if len(matches) == 0:
            self.hardwared_temp = '---'
            return
        
        if len(matches) > 1:
            self.hardwired_temp = '???'
            return
        self.hardwired_temp = None
        self.sensor = '/sys/class/thermal/%s/temp' % matches[0]

    def read_degrees_centigrade(self):
        if self.hardwired_temp is not None:
            return self.hardwired_temp

        with open(self.sensor) as src:
            raw = src.read()
        if len(raw) < 1:
            return ':('
        return '%.1f' % (int(raw)/1000.0)
        

def fetch():
    with open('/etc/issue') as src:
        issue = src.read()

    if 'Raspbian' in issue:
        return linux_thermal_zone('bcm2835_thermal')
    
    return linux_thermal_zone('x86_pkg_temp')

    
    
