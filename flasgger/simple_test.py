"""
# create a virtualenv
mkvirtualenv test_api

# install dependencies
pip install flask
pip install flasgger

# run the following script
python simple_test.py
"""
from flask import Flask, jsonify, request
from base import Swagger
from flask.views import View

app = Flask(__name__)

Swagger(app)


@app.route("/recs", methods=['GET'])
def recs():
    """
    A simple test API
    This endpoint does nothing
    Only returns "test"
    ---
    tags:
      - testapi
    parameters:
      - name: size
        in: query
        type: string
        description: size of elements
    responses:
      200:
        description: A single user item
        schema:
          id: return_test
          properties:
            result:
              type: string
              description: The test
              default: 'test'
    """
    size = int(request.args.get('size', 1))
    return jsonify({"result": "test" * size})


class Foo(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        """
        A simple test API
        This endpoint does nothing
        Only returns "test"
        ---
        tags:
          - rohit
        parameters:
          - name: size
            in: query
            type: string
            description: size of elements
        responses:
          200:
            description: A single user item
            schema:
              id: return_test
              properties:
                result:
                  type: string
                  description: The test
                  default: 'test'
        """
        size = int(request.args.get('size', 1))
        return jsonify({"result": "test" * size})


app.add_url_rule('/dispatch_request', view_func=Foo.as_view('foo'))
app.run(debug=True)
