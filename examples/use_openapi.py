"""
In this example `openapi` version is used instead of `swagger` version.
"""
from flask import Flask
from flasgger import Swagger

app = Flask(__name__)
swag = Swagger(app, config={
    'headers': [],
    'specs': [
        {
            'endpoint': 'apispec',
            'route': '/apispec.json'
        }
    ],
    'openapi': '3.0.1'
})


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    for spec in specs_data.values():
        assert 'openapi' in spec
        assert '3.0.1' == spec['openapi']
        assert 'swagger' not in spec


if __name__ == '__main__':
    app.run(debug=True)
