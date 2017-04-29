# Hooklib: Easy Source Control Hooks

Hooklib is an Apache2 Licensed library, in Python, to help people write hooks for source control:
- **SCM Agnostic:** hooks can work with different SCM (git, svn, hg), write your hook once and they work on other SCMs
- **Simple API:** don't learn the secret commands to peek inside your source control system, all you need is accessible and computed on the fly
- **Parallel/Sequential execution:** run your hooks in parallel or sequentially

Supported hooks phases:

Phase name          | SCM | Available fields
------------------- | ------------- | ----------------
applypatch-msg  | Git | reporoot, head, messagefile
pre-applypatch  | Git | reporoot, head
post-applypatch  | Git | reporoot, head
pre-commit  | Git | reporoot, head
prepare-commit-msg  | Git | reporoot, head, messagefile, mode, sha
commit-msg  | Git | reporoot, head, messagefile
post-commit  | Git | reporoot, head
pre-rebase  | Git | reporoot, head, upstream, rebased
pre-push  | Git | reporoot, head, revstobepushed
pre-receive  | Git | reporoot, head, receivedrevs
update  | Git, Hg | reporoot(git), head(git), refname(git) old(git), new(git), rev(hg)
post-receive  | Git | reporoot, head, receivedrevs
post-update  | Git | reporoot, head, revs
pre-auto-gc  | Git | reporoot, head

Currently only supports git and hg


Example 1: gate commit on commit message format
-
Feel free to compare this to how you would do this without this library: https://git-scm.com/book/en/v2/Customizing-Git-An-Example-Git-Enforced-Policy

This hooks works for both git and hg:
 - for git: put it in .git/hooks/update and make it executable for git
 - for hg: put it wherever your want and reference it from your hg config

```python
#!/usr/bin/python
from hooklib import basehook, runhooks

class commmitmsggatinghook(basehook):
   def check(self, log, revdata):
       for rev in revdata.revs:
           if not 'secretmessage' in revdata.commitmessagefor(rev):
               log.write("commit message must contain 'secretmessage'")
               return False
       return True

runhooks('update', hooks=[commmitmsggatinghook])
```

Example 2: only authorize push to master
-

_Contrary to the example 1, here we reference 'refs/heads/master', a git concept => this hook wouldn't work without code change for hg._
Save the following file under .git/hooks/update and make it executable to test it: 
 ```python
 #!/usr/bin/python
 from hooklib import basehook, runhooks
  
 class mastergatinghook(basehook):
    def check(self, log, revdata):
       pushtomaster = revdata.refname == 'refs/heads/master'
       if not pushtomaster:           
          log.write("you can only push master on this repo")
          return False
       else:
          return True
  
 runhooks('update', hooks=[mastergatinghook])
  ```
  
Example 3: parallel execution
-
Save the following file under .git/hooks/post-update and make it executable to test it: 
  ```python
  #!/usr/bin/python
  from hooklib import basehook, runhooks
  import time
  
  class slowhook(basehook):
     def check(self, log, revdata):
         time.sleep(0.1)
         return True
  
  class veryslowhook(basehook):
     def check(self, log, revdata):
         time.sleep(0.5)
         return True

  # should take roughly as long as the slowest, i.e. 0.5s
  runhooks('post-update', hooks=[slowhook]*200+[veryslowhook], parallel=True)
  ```

Example 4: client side commit message style check
-
The following hooks checks on the client side that the commit message follows the format: "topic: explanation"
I have it enabled for this repo to make sure that I respect the format I intended to keep.
Save the following file under .git/hooks/commit-msg and make it executable to test it:
  ```python
  #!/usr/bin/python 
  from hooklib import basehook, runhooks 
  import re
  
  class validatecommitmsg(basehook): 
       def check(self, log, revdata): 
  	with open(revdata.messagefile) as f:
  	    msg = f.read()
  	if re.match("[a-z]+: .*", msg):
  	    return True
  	else:
  	    log.write("validatecommit msg rejected your commit message")
  	    log.write("(message must follow format: 'topic: explanation')")
  	    return False
  
  runhooks('commit-msg', hooks=[validatecommitmsg])  
  ```

Example 5: validate unit test passing before commiting
-

The following hooks checks on the client side that the commit about to be made passes all unit tests.
I have it enabled for this repo to make sure that I respect the format I intended to keep.
Save the following file under .git/hooks/pre-commit and make it executable to test it:
 
  ```python
  from hooklib import basehook, runhooks 
  import os
  import subprocess
  
  class validateunittestpass(basehook): 
       def check(self, log, revdata): 
          testrun = "python %s/hooktests.py" % revdata.reporoot
          ret = subprocess.call(testrun, 
                                shell=True,
                                env={"PYTHONPATH":revdata.reporoot})
          if ret == 0:
              return True
          else:
              log.write("unit test failed, please check them")
              return False
  
  runhooks('pre-commit', hooks=[validateunittestpass])  
  ```


Installation
-
You can use pip:
```
sudo pip install mercurial
sudo pip install hooklib
```

Or install it directly from the repo:
```
git clone https://github.com/charignon/hooklib.git
sudo python setup.py install
sudo pip install mercurial
```

User Guide
-

Once you have installed the library, you can start writing you first hook.
It is easy to just get started by copy-pasting one of the examples.
A hook should is a python class that derives from the base class `basehook`.

The hook's `check(self, log, revdata)` instance function will get called with a `log` and a `revdata` object:
- The `check` function should return True if the hook passes and False otherwise.
- The `log` object can be used to send feedback to the user, for example, if your hook rejects a commit, you can explain what justifies the rejection. You can use `log.write(str)` as shown in the examples
- The `revdata` object allows you to get all the information that you need about the state of the repo.

For example, if you are writing a `commit-msg` hook, `revdata.messagefile` will be the filename of the file containing the commit message to validate.
You can get the complete list of the accessible fields by looking at the documentation of the class for the hook in question.

If you want to know the field available in `revdata` for the `pre-receive` hook for git. Look into `hooklib_git.py`, find the class `gitprereceiveinputparser` and look at its pydoc:

In a python shell:

```
>>> from hooklib_git import *
>>> help(gitprereceiveinputparser)
Help on class gitprereceiveinputparser in module hooklib_git:

class gitprereceiveinputparser(gitreceiveinputparser)
 |  input parser for the 'pre-receive' phase
 |
 |  available fields:
 |  - reporoot (str) => root of the repo
 |  - receivedrevs =>
 |      (list of tuples: (<old-value> <new-value> <ref-name>))
 |  - head (str) => sha1 of HEAD
 |
...
```

Bugzilla 5.0 API
-
To develop on the Bugzilla API you will need to add a secrets.py file in this project directory which contains your user specific login details and domain URL which will be used for testing and eventually usage of this extension.

Adding Bugzilla.py file which contains work in progress class which can interface with the Bugzilla 5.0 API for getting bug status's and updating bug data. 

The goal of this is to eventually create a precommit hook which can update teh status of a bug automatically from a commit message. To in crease developer productivity. 

There once was such an extension for mercurial but unfortunately it seems to be broken when using the Bugzilla 5.0 or later.

Your secrets.py file should look like this: 

```
secrets = {
    'USERNAME': 'foo.bar@gmail.com',
    'PASSWORD': 'foobar123',
    'BUGZILLA_URL': 'https://landfill.bugzilla.org/bugzilla-5.0-branch/'
    }
```

Note: if you would like to do some testing, you can create a test account at https://landfill.bugzilla.org


Contributing
-
Before sending a Pull Request please run the tests:

- To run the unit tests, simply call `python hooktests.py`, let's keep the unit test suite running under 1s
  You have to install mock to run the tests: `sudo pip install mock==1.0.0`
- To run the integration tests, download run-tests.py from the mercurial repo "https://selenic.com/hg/file/tip/tests/run-tests.py"
Then you can run the tests with `python run-tests.py test-git.t -l` (I only have tests for git so far)


Clocker - Time Logger
- 

## TODO

+ add function to reset the time_sheet for a specific project
+ add command line support for usability
+ getters for duration of a project so that it can be autopopulated to a commit message for example
