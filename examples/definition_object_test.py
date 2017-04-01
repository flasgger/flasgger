"""
A test using simple class based definitions
"""
from flask import Flask, jsonify, request
from flask.views import View

from flasgger import Swagger

app = Flask(__name__)

# Flasgger is initialized like a standard flask extension.
# You can also use .init_app() with the "app factory" pattern.
swag = Swagger(app)


# Definitions can be registered as objects or functions.
# Docstring lines (before '---') are used as the description.
# YAML after '---' defines the Swagger definition schema.
@swag.definition('return_test_1')
class ReturnTest(object):
    """
    test return
    ---
    properties:
      result:
        type: string
        description: The test
        default: 'test1'
    """

    def __init__(self, size):
        self.size = int(size)

    def dump(self):
        return {"result": "test1" * self.size}


@swag.definition('return_test_2')
def return_test(size):
    """
    another test return
    ---
    properties:
      result:
        type: string
        description: The test
        default: 'test2'
    """
    size = int(size)

    return {"result": "test2" * size}


# Flask endpoints with flasgger docstrings are automatically registered.
# The first line of the docstring is used as the summary/
# The following lines (before '---') are used as the description.
# YAML after '---' defines the Swagger path schema.
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
          $ref: '#/definitions/return_test_1'
    """
    message = ReturnTest(request.args.get('size', 1)).dump()
    return jsonify(message)


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
              $ref: '#/definitions/return_test_2'
        """
        message = return_test(request.args.get('size', 1))
        return jsonify(message)


app.add_url_rule('/dispatch_request', view_func=Foo.as_view('foo'))

if __name__ == "__main__":
    app.run(debug=True)
