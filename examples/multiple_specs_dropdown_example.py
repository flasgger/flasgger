"""
In this example a spec name is provided in order to trigger SwaggeUI's dropdown list of specs.
"""
from flask import Flask, jsonify
try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus
from flasgger import Swagger
from flasgger.utils import swag_from


swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "version": "0.0.1",
            "title": "Api v1",
            "name": "v1",
            "endpoint": 'v1_spec',
            "description": 'This is the version 1 of our API',
            "route": '/v1/spec',
            "rule_filter": lambda rule: rule.rule.startswith('/v1/'),
        },
        {
            "version": "0.0.2",
            "title": "Api v2",
            "name": "v2",
            "description": 'This is the version 2 of our API',
            "endpoint": 'v2_spec',
            "route": '/v2/spec',
            "rule_filter": lambda rule: rule.rule.startswith('/v2/'),
        }
    ],
    "static_url_path": "/flasgger_static",
}

app = Flask(__name__)
swag = Swagger(app, config=swagger_config)



@app.route('/v1/hello')
def v1_hello():
    """
    A test view

    ---
    responses:
      200:
        description: OK
    """
    return jsonify(hello="world")


@app.route('/v2/hello')
def v2_hello():
    """
    A test view v2

    ---
    responses:
      200:
        description: OK
    """
    return jsonify(hello="world")


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    assert client.get('/apidocs/').status_code == HTTPStatus.OK


if __name__ == '__main__':
    app.run(debug=True)
