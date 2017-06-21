"""
This tests the use of `decorator` package with Flasgger
"""
from decorator import decorator
from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swag = Swagger(app)


@decorator
def trace(f, *args, **kw):
    kwstr = ', '.join('%r: %r' % (k, kw[k]) for k in sorted(kw))
    print("calling %s with args %s, {%s}" % (f.__name__, args, kwstr))
    return f(*args, **kw)


@app.route('/')
@trace
def index():
    """
    This example tests decorator package
    Should not break in Python 2.7+
    ---
    responses:
      200:
        description: Yeah it works
    """
    return jsonify({'data': 'It works'})


if __name__ == '__main__':
    app.run(debug=True)

