# Miscelaneous hook ideas and prototype implementations 
# to validate idea
import time
import re

class Clocker(object):
        
    """
    Clock in and clock out of your work that your doing and store 
    times in a temp file which clears after each clocking out, if
    dirty it is then commit will not be allowed
    """
  
    def __init__(self, clk_file_name):
        super(Clocker, self).__init__()
        self._clk_file_name = clk_file_name
        
    
    def clock_in(self):
        """ 
        Gets the current time and writes into 
        the clk_file as the Start Time
        """
        # get the time in epochs
        clkin = time.time()
        out = 'Start Time: {0}\n'.format(clkin)
        with open(self._clk_file_name, 'w') as f:
            f.write(out)
    
    def time_diff(self, tin, tout):
        ltin = time.localtime(tin)
        ltout = time.localtime(tout)
        return (ltout.tm_hour-ltin.tm_hour, ltout.tm_min-ltin.tm_min, ltout.tm_sec-ltin.tm_sec)
    
    def clock_out(self):
        patt = re.compile('[Start Time:][0-9.]+')
        clkout = time.time()
        clkin = ''
    
        with open(self._clk_file_name, 'rw') as f:
            contents = f.read()
            clkin = re.findall(patt, contents)[0]
            clkin = float(clkin)
            print contents
            print 'Found: {0}'.format(clkin)
            f.write('')
        print clkin
        if clkin:
            tdiff = self.time_diff(clkin, clkout)    
        return tdiff
        
if __name__ == '__main__':
    print 'Tesing:'
    clk_file = '.clocker'
    clckr = Clocker(clk_file)
    clckr.clock_in()
    with open(clk_file, 'r') as f:
        print f.read()
    # Sleep a few seconds
    time.sleep(1)
    tm_clocked = clckr.clock_out()
    print 'Time Difference: {0}'.format(tm_clocked)
    