#!/usr/bin/python
import argparse
from collections import OrderedDict

from flask import Flask, render_template
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from flasgger import __version__
from flasgger.utils import get_examples

app = Flask(__name__)

examples = OrderedDict({
    '/{0}'.format(mod.__name__.split('.')[-1]): mod
    for mod in sorted(get_examples(), key=lambda x: x.__name__)
})


@app.route('/')
def index():
    return render_template('flasgger.html',
                           examples=examples,
                           version=__version__)


for example, mod in examples.items():
    if hasattr(mod.app, 'swag'):
        mod.app.swag.config['basePath'] = example

application = DispatcherMiddleware(
    app,
    {name: mod.app for name, mod in examples.items()}
)


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
