"""
This script is a WSGI configuration/setup file suitable for use in
deploying the Flasgger demo_app to PythonAnywhere, https://www.pythonanywhere.com/ .

To deploy:

- Create a PythonAnywhere account if you don't already have one. Replace <username>
  below with your PythonAnywhere username.
- Visit https://www.pythonanywhere.com/user/<username>/webapps and create a new/default
  web app, using Manual Configuration and Python 3.6.
- Confirm you can access the Hello, World! page at https://<username>.pythonanywhere.com/ .
- Visit https://www.pythonanywhere.com/user/<username>/consoles/ and create a new bash console.
- From your home directory /home/<username>, run:
      git clone https://github.com/rochacbruno/flasgger.git
  ... or use another fork.
- cd ~/flasgger, then change to whichever branch you want to use.
- Create a new virtual environment:
      mkvirtualenv --python=python3.6
- Run: pip3 install -r requirements.txt -r requirements-dev.txt
- cd /var/www
- rm ${USERNAME}_pythonanywhere_com_wsgi.py
- ln -s ~/flasgger/etc/pythonanywhere/pythonanywhere_com_wsgi.py ${USERNAME}_pythonanywhere_com_wsgi.py
- Go to the web app console at https://www.pythonanywhere.com/user/<username>/webapps .
- Modify the configuration:
  - Make the source path /home/<username>/flasgger
  - Make the working directory /home/<username>/flasgger
  - Change the virtual env path to /home/<username>/.virtualenvs/flasgger
- Reload the web app.
- Visit https://<username>.pythonanywhere.com/ and you should see the demo_app landing page.
- If an error occurs, review the log files.
"""
import os
import subprocess
import sys

home = os.path.expanduser("~")
path = os.environ.get('FLASGGER_HOME') or home + '/flasgger'

subprocess.check_call(['git', 'pull', path])

if path not in sys.path:
    sys.path.append(path)

from demo_app.app import application
