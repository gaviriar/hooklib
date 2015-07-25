# hooklib
Python hook helper library for git, hg, subversion ... Abstract your hooks, run them in parallel, make your life easier!

You can see the tests for example use.
Currently only supports GIT.


Contributing
-

To run the unit tests, simply call `python hooktests.py`

To run the integration tests, download run-tests.py from the mercurial repo "https://selenic.com/hg/file/tip/tests/run-tests.py"
Then you can run the tests with `python run-tests.py test-integration.t -l`

Minimal example 1: only authorize push to master
-

Save the following file under .git/hooks/update and make it executable to test it: 
 ```python
 #!/usr/bin/python
 from hooklib import basehook, runhooks
  
 class mastergatinghook(basehook):
    def check(self, log, revdata):
       pushtomaster = revdata['name'] == 'refs/heads/master'
       if not pushtomaster:           
          log.write("you can only push master on this repo")
          return False
       else:
          return True
  
 runhooks('update', hooks=[mastergatinghook])
  ```
  
Minimal example 2: running 50 post-update hooks in parallel
-
Save the following file under .git/hooks/post-update and make it executable to test it: 
  ```python
  from hooklib import basehook, runhooks
  import time
  
  class slowhook(basehook):
     def check(self, log, revdata):
         time.sleep(0.1)
         return True
  
  runhooks('post-update', hooks=[slowhook]*200, parallel=True)
  ```
