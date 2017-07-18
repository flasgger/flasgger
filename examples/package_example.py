# coding: utf-8
"""
This tests the use of a view coming from installed
package.
"""

from flask import Flask, jsonify
from flasgger import Swagger
from flasgger_package import package_view


app = Flask(__name__)
swag = Swagger(app)

app.add_url_rule(
    '/v1/decorated/<username>',
    view_func=package_view
)


@app.route('/v2/decorated/<username>')
def package_view_2(username):
    """
    This is the summary defined in yaml file
    First line is the summary
    All following lines until the hyphens is added to description
    the format of the first lines until 3 hyphens will be not yaml compliant
    but everything below the 3 hyphens should be.
    ---
    tags:
      - users
    import: "flasgger_package/parameters.yml"
    responses:
      200:
        description: A single user item
        schema:
          id: rec_username
          properties:
            username:
              type: string
              description: The name of the user
              default: 'steve-harris 2'
    """
    return jsonify({'username': username})


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
