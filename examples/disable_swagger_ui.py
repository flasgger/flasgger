"""
In this example Swagger UI is disabled.
"""
from flask import Flask
try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus
from flasgger import Swagger

swagger_config = {
    'headers': [
    ],
    'specs': [
        {
            'endpoint': 'apispec',
            'route': '/apispec.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda tag: True,
        }
    ],
    'swagger_ui': False
}

app = Flask(__name__)
swag = Swagger(app, config=swagger_config)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """

    assert not specs_data
    assert client.get('/apidocs/').status_code == HTTPStatus.NOT_FOUND
    assert client.get('/apispec.json').status_code == HTTPStatus.OK

if __name__ == '__main__':
    app.run(debug=True)
