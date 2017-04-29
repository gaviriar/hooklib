import requests as req
# Logging in through API


def DEBUG(xxx):
    pass
    #    print xxx
# All future requests will require this authentication token as a parameter


class Bugzilla(object):
    """docstring for Bugzilla"""
    comment_errs = [54, 100, 101, 109, 113,
                    114, 140, 129, 130, 131, 132,
                    133, 134, 140, 601, 603, 604]
    timeout = 5.0

    DEFAULT_URL = 'https://landfill.bugzilla.org/bugzilla-5.0-branch/'

    def __init__(self, bz_url=DEFAULT_URL, bug_id=-1):
        # super(Bugzilla).__init__()
        self._token = dict()
        self._bz_url = req.compat.urljoin(bz_url, 'rest/')
        self._bug_url = req.compat.urljoin(self._bz_url, 'bug/')
        self._bug_id = bug_id

    def login(self, username, password):
        url = req.compat.urljoin(self._bz_url, 'login')
        login_params = {'login': username, 'password': password}
        DEBUG(url)
        DEBUG(login_params)
        try:
            res = req.get(url, login_params,  timeout=Bugzilla.timeout)
            res.raise_for_status()
        except req.exceptions.BaseHTTPError as err:
            print err
            return False

        # if no exception is raised then safe to process the response
        self._token = {'token': res.json()['token']}
        return res

    @property
    def bug_id(self):
        ''' getter property of bug_id'''
        return self._bug_id

    @bug_id.setter
    def bug_id(self, bug_id):
        """
        Sets the bug_id of the class and returns the
        respones from a GET request to that bug
        """
        self._bug_id = str(bug_id)
        endpoint_url = '/'.join(['bug', self._bug_id])
        self._bug_url = req.compat.urljoin(self._bz_url, endpoint_url)
        DEBUG(self._bug_url)

    def bug(self, bug_id=None):
        """
        Returns the GET response from bug_id
        """
        if bug_id:
            self.bug_id = bug_id

        params = {}
        params.update(self._token)
        try:
            res = req.get(self._bug_url, params, timeout=Bugzilla.timeout)
            res.raise_for_status()
            return res
        except req.exceptions.HTTPError as err:
            print err
            return False

    def to_bugzilla_status(valeo_status):
        """
        @todo need to identify if this function is really necessary?
        Helper function to convert Bugzilla status
        updates in commit message to expected status
        values in status fiel
        """

        if valeo_status == 'started':
            return 'Opened'
        elif valeo_status == 'complete':
            return 'complete'
        elif valeo_status == 'fixed':
            return 'fixed'
        elif valeo_status == 'tested':
            return 'tested'

    def comment(self, params=None, bug_id=None,
                username=None, password=None, work_time=-1):
        """
        Update comment on bug
        @todo: Need to be able to parse changeset to add to comment
        @todo: Check comment and verify bug_id is there and additional info

        :return response from HTTP POST or False if an error occured
                @todo should add a feature to support exceptions if an
                error condition happens
        @todo what is better? handling exceptions inside the code or raising
              them to the next level
        """
        if bug_id:
            self.bug_id = bug_id

        if username and password:
            self.login(username, password)

        if params['comment']:
            ept_url = '/'.join(['bug', self._bug_id, 'comment'])
            url = req.compat.urljoin(self._bz_url, ept_url)
            DEBUG(self._bz_url)
            DEBUG(ept_url)
            DEBUG('Login_url: ' + url)
            DEBUG(url)
            DEBUG(params)

            params.update(self._token)
            res = req.post(url, params)
            # Raise exception if error in processing
            res.raise_for_status()
            return res
        else:
            ERROR('The comment is invalid')
            return False

        # This is dead code
        # Set the desired fields to update
        params = dict()
        params['comment'] = params
        params['is_private'] = False
        params['is_markdown'] = True
        if work_time != -1:
            params['work_time'] = work_time
        else:
            print 'You did not specify a work time'
        # Add the access token to params
        params.update(self._token)
        res = req.post(url, params, timeout=Bugzilla.timeout)
        # Should handle the response gracefully, see below(not very happy)
        return res

    def update(self, bug_id, comment, work_time=-1, status=False):
        """
        A very similar function to comment() above except.
        Need to verify wether we need this function at all....
        for now UNTESTED
        """
        # change bug status
        self.bug(bug_id)
        url = req.compat.urljoin(self._bug_url, 'bug/')
        # Set the desired fields to update
        params = dict()
        params['comment'] = {
                'body': comment,
                'is_private': False,
                'is_markdown': False
                }
        if status:
            params['status'] = self.to_bugzilla_status(status)
        if work_time != -1:
            params['work_time'] = work_time
        # Add the access token to params
        params.update(self._token)
        res = req.put(url, params, timeout=Bugzilla.timeout)
        res.raise_for_status()
        return res

    def is_closed(self, bug_id):
        """
        @todo need to do this function
        """
        self.bug(bug_id)
        url = req.compat.urljoin(self.bug_url, 'bug')


def parseCommitMessage(hg_msg):
    """
    Function which parses mercurial commit
    messages to obtain bug id and reformat
    the text removing any new lines
    """
    import re
    patt = re.compile('(#)([0-9]+)')
    match = patt.search(hg_msg)

    if match:
        return match.group(2), hg_msg
    else:
        return False

    # Ability to get a list of c1omments for a bug specified?
if __name__ == '__main__':
    from secrets import *
    LOGIN_PARAMS = {
        'login': secrets['USERNAME'], 
        'password': secrets['PASSWORD']
        }
    BUGZILLA_URL = secrets['BUGZILLA_URL']
    bz = Bugzilla(BUGZILLA_URL)
    login_res = bz.login(LOGIN_PARAMS['login'], LOGIN_PARAMS['password'])
    BUG_GT = 36912

    # The following code section is an example of how this module can be used
    # 1) We will parse a dummy commit message from a text file, and search for
    #    a pattern specified in parseCommitMessage()
    #
    # 2) We will then try to update the bug with a comment containing
    #    the contents of the commit message
    with open('hg_comment.txt', 'r') as f:
        commit_message = f.read()

    if login_res:
        # Comment Test
        BUG, commit_message = parseCommitMessage(commit_message)
        BUG = int(BUG)

        # Hijack the BZ id to test
        BUG = BUG_GT
        params = {}
        params['comment'] = commit_message

        bz.bug_id = BUG
        try:
            res = bz.comment(params)
            msg = 'Comment succesfully submitted:\n{}'.format(res.json())
        except req.exceptions.HTTPError as err:
            msg = 'Failed to update comment\n{}'.format(err)
        # @todo need to check the response pattern and handle error cases

        print msg
    else:
        print 'Failed login'
