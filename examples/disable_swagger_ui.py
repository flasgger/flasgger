"""
In this example Swagger UI is disabled.
"""
from flask import Flask

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
    'swagger_ui': False,
    'specs_route': ''
}

DEFAULT_CONFIG = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": False,
    "specs_route": "/apidoc/"
}

app = Flask(__name__)
swag = Swagger(app, config=DEFAULT_CONFIG)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    
    assert not specs_data

if __name__ == '__main__':
    app.run(debug=True)
