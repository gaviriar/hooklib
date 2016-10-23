import requests as req
from flask.globals import request
from findertools import comment
# Logging in through API
def DEBUG(xxx):
    print xxx
# All future requests will require this authentication token as a parameter
class Bugzilla(object):
    """docstring for Bugzilla"""
    comment_errs = [54,100,101,109,113,114,140,129,130,131,132,133,134,140,601,603,604]
    timeout = 2.0
    
    def __init__(self, bzUrl='https://landfill.bugzilla.org/bugzilla-5.0-branch/', bug_id=-1):
        # super(Bugzilla).__init__()
        self._token = dict()
        self._bzUrl = req.compat.urljoin(bzUrl, 'rest/')
        self._bug_url = req.compat.urljoin(self._bzUrl, 'bug/')
        self._bug_id = bug_id
        
    def login(self, username, password):
        url = req.compat.urljoin(self._bzUrl, 'login')
        login_params = {'login': username, 'password': password}
        DEBUG(url)
        DEBUG(login_params)
        res = req.get(url, login_params,  timeout=Bugzilla.timeout)
        if res.status_code == 200:
            self._token = {'token': res.json()['token']}
            return res
        else:
            return False

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
        self._bug_url = req.compat.urljoin(self._bzUrl, endpoint_url)
        DEBUG(self._bug_url)        

    def bug(self):
        """
        Returns the GET response from bug_id
        """
        params = {}
        params.update(self._token)
        res = req.get(self._bug_url, params, timeout=Bugzilla.timeout)
        return res
    
    def to_bugzilla_status(valeo_status):
        """
        Helper function to convert Bugzilla status 
        updates in commit message to expected status 
        values in status field
        """
        
        if valeo_status == 'started':
            return 'Opened'
        elif valeo_status == 'complete':
            return 'complete'
        elif valeo_status == 'fixed':
            return 'fixed'
        elif valeo_status == 'tested':
            return 'tested'

    def comment(self, comment = None, bug_id = None, work_time=-1):
        """
        Update comment on bug
        @todo: Need to be able to parse changeset to add to comment
        @todo: Check comment and verify bug_id is there and additional info
        """
        if bug_id:
            self.bug_id = bug_id
        
        if comment['comment']:
            ept_url = '/'.join(['bug', self._bug_id, 'comment'])
            url = req.compat.urljoin(self._bzUrl, ept_url)
            DEBUG(self._bzUrl)
            DEBUG(ept_url)
            DEBUG('Login_url: ' + url)
            comment.update(self._token)
            res = req.post(url, comment)
            
            return res, self.is_bug_error(res.json())
        else: 
           ERROR('The comment is invalid')
           return False 
        
        # This is dead code
        # Set the desired fields to update
        params = dict()
        params['comment'] = comment
        params['is_private'] = False
        params['is_markdown'] = True
        if work_time != -1:
            params['work_time'] = work_time
        else:
            print 'You did not specify a work time'
        # Add the access token to params
        params.update(self._token)
        print url
        print params
        res = req.post(url, params, timeout=Bugzilla.timeout)
        # Should handle the response gracefully, see below(not very happy)
        return res

    def update(self, bug_id, comment, work_time=-1, status=False):
        # change bug status
        bug(bug_id)
        url = req.compat.urljoin(self._bug_url,'bug/')
        # Set the desired fields to update
        params = dict()
        params['comment'] = {'body': comment, 'is_private': False, 'is_markdown': False}
        if status:
            params['status'] = to_bugzilla_status(status)
        if work_time != -1:
            params['work_time'] = work_time
        # Add the access token to params
        params.update(login_params)
        res = req.put(url, params, timeout=Bugzilla.timeout)
        return is_bug_error(res)

    def is_closed(self, bug_id):
        bug(bug_id)
        url = req.compat.urljoin(self.bug_url, 'bug')

    def is_bug_error(self,res_dict):
        """
        Returns true if the input res_dictponse (dictionary) 
        contains a code key which indicates that an 
        error occured in the REST request
        :res_dict The response from the HTTP request when 
        converted to json e.g. res.json()
        :return True if error response, False otherwise
        """
        ret = False
        if 'code' in res_dict.keys():
            if res_dict['code'] in self.comment_errs:
                DEBUG('Is Error')
                raise Exception('Bug Error:', res_dict)
                return True
#         except Exception as inst:
#             txt, err = inst.args
#             print txt + ' ' + err
#         return ret
        return False

    # Ability to get a list of comments for a bug specified?
if __name__ == '__main__':
    from secrets import *
    LOGIN_PARAMS = {
        'login': secrets['USERNAME'], 
        'password': secrets['PASSWORD']
        }
    BUGZILLA_URL = secrets['BUGZILLA_URL']
    bz = Bugzilla(BUGZILLA_URL)
    login_res = bz.login(LOGIN_PARAMS['login'], LOGIN_PARAMS['password'])
    BUG = 36912
    if login_res:
        print login_res
        bz.bug_id = BUG
        #print bz.bug_id
        #res = bz.bug()
        
        #print res.json()
        # Comment Test
        comment = {}
        comment['comment'] = 'This is a test comment from the Buzzilla Python class'
        res = bz.comment(comment)
        print res.content
        
#         print bz.comment(BUG, comment='Helo commenting from the Bugzilla Class').json()
    else: 
        print 'Failed login'