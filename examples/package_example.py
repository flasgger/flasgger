# coding: utf-8
"""
This tests the use of a view coming from installed
package.
"""

from flask import Flask
from flasgger import Swagger
from flasgger_package import package_view


app = Flask(__name__)
swag = Swagger(app)

app.add_url_rule(
    '/v1/decorated/<username>',
    view_func=package_view
)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    for url, spec in specs_data.items():
        assert 'rec_username' in spec['definitions']
        assert 'users' in spec['paths'][
            '/v1/decorated/{username}'
        ]['get']['tags']


if __name__ == "__main__":
    app.run(debug=True)
