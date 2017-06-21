"""
Ensure that top-level vendor extension config is preserved
"""

from flasgger import Swagger
from flask import Flask, jsonify

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Vendor extension test',
    'uiversion': 2,
    'x-groupTag': 'Test',
}
swag = Swagger(app)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    assert 'x-groupTag' in specs_data['/apispec_1.json']
    assert specs_data['/apispec_1.json']['x-groupTag'] == 'Test'


if __name__ == "__main__":
    app.run(debug=True)
