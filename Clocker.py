# Miscelaneous hook ideas and prototype implementations
# to validate idea
import time
import json
from datetime import timedelta
from pprint import pprint


class Clocker(object):
    """
    Clock in and clock out of your work that your doing and store
    times in a temp file which clears after each clocking out, if
    dirty it is then commit will not be allowed
    """

    def __init__(self, clk_file_name):
        super(Clocker, self).__init__()
        self._clk_file_name = clk_file_name
        self._timesheet = None

        self.load_timesheet()

    def load_timesheet(self):
        with open(self._clk_file_name, 'r') as f:
            self._timesheet = json.load(f)

    def dump_timesheet(self):
        with open(self._clk_file_name, 'w') as f:
            json.dump(self._timesheet, f)

    def exists(self, project_name):
        """
        :details Function verifies that the project name exists
                 in the timesheet list, if it does not it will
                 prompt the user to create project or cancel request

        """
        for idx, p in enumerate(self._timesheet):
            # convert from unicode to string
            if str(p["name"]) == project_name:
                return True, idx

        return False, None

    def list(self):
        for p in self._timesheet:
            print p["name"]

    def get_work(self):
        self.load_timesheet()
        for p in self._timesheet:
            print_project(p)

    def clock_in(self, project_name=None):
        """
        Gets the current time and writes into
        the clk_file as the Start Time
        """
        clkin = time.time()
        self.load_timesheet()
        exists, idx = self.exists(project_name)

        if exists:
            self._timesheet[idx]["clock_in"] = clkin
            self.dump_timesheet()
            print 'Start Time: {0}\n'.format(time.asctime(time.localtime(clkin)))
            # pprint(self._timesheet)
        else:
            msg = "Project {} does not exist in timesheet, would you like to create it? [Y/n]"
            # @todo need to add user input prompt
            print msg
            return False

    def clock_out(self, project_name=None):
        clkout = time.time()
        self.load_timesheet()
        exists, idx = self.exists(project_name)

        if exists and self._timesheet[idx]["clock_in"]:
            clkin = self._timesheet[idx]["clock_in"]
            tdiff = clkout - clkin
            self._timesheet[idx]["duration"] += tdiff
            self._timesheet[idx]['clock_out'] = clkout
            self.dump_timesheet()
            return tdiff
        else:
            return False


"""
Helper funcitons
"""


def print_project(p):
    dur_td = timedelta(p['duration'])
    secs = dur_td.seconds
    hrs = secs // 3600
    secs = secs % 3600
    mins = secs // 60
    secs = secs % 60
    duration_str = '{} {}:{}:{}'.format(dur_td.days, hrs, mins, secs)

    out = """
        Project: {}
        Duration: {}
        Clock In: {}
        Clock Out: {}
    """.format(p['name'], duration_str,
               time.asctime(time.localtime(p['clock_in'])),
               time.asctime(time.localtime(p['clock_out'])))
    print out


if __name__ == '__main__':
    print 'Tesing:'
    clk_file = '.clocker'
    timesheet = 'timesheet.json'

    clckr = Clocker(timesheet)
    clckr.clock_in(project_name='beocean')

    # Sleep a few seconds
    time.sleep(1)
    tm_clocked = clckr.clock_out(project_name='beocean')
    clckr.get_work()
