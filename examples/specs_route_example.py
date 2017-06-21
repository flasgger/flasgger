"""
In this example a custom specs_route is set.
"""
from flask import Flask
try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus
from flasgger import Swagger

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'specifications',
            "route": '/specifications.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "specs_route": "/documentation/swagger/"
}

app = Flask(__name__)
swag = Swagger(app, config=swagger_config)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    assert client.get('/documentation/swagger/').status_code == HTTPStatus.OK
    assert specs_data.get('/specifications.json') is not None


if __name__ == '__main__':
    app.run(debug=True)
