#!/usr/bin/python
import os
import sys
import argparse
from werkzeug.serving import run_simple
from flasgger import app


# If running on PAAS such as OpenShift or heroku may require venv activation
if os.environ.get('OPENSHIFT_HOMEDIR', None):
    sys.path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR']))
    sys.path.insert(0, os.path.dirname(__file__) or '.')
    if os.path.exists(os.path.join(
            os.environ['OPENSHIFT_HOMEDIR'], "python-2.6")):
        py_dir = os.path.join(
            os.environ['OPENSHIFT_HOMEDIR'], "python-2.6")
    else:
        py_dir = os.path.join(os.environ['OPENSHIFT_HOMEDIR'], "python")

    virtenv = py_dir + '/virtenv/'
    py_cache = os.path.join(virtenv, 'lib', '2.6', 'site-packages')
    os.environ['PYTHON_EGG_CACHE'] = os.path.join(py_cache)
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')

    try:
        if sys.version_info >= (3, 0):
            with open(virtualenv) as f:
                code = compile(f.read(), virtualenv, 'exec')
                exec(code, globals(), locals())
        else:
            execfile(virtualenv, dict(__file__=virtualenv))  # noqa
    except IOError:
        pass

application = app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run App for WSGI")
    parser.add_argument('-p', '--port', help='App Port')
    parser.add_argument('-i', '--host', help='App Host')
    parser.add_argument('-r', '--reloader', action='store_true',
                        help='Turn reloader on')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Turn debug on')
    args = parser.parse_args()
    run_simple(
        args.host or '0.0.0.0',
        int(args.port) if args.port else 5000,
        application,
        use_reloader=args.reloader or False,
        use_debugger=args.debug or False,
    )
