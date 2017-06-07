"""
A test to ensure routes from Blueprints are swagged as expected.
"""
from flask import Blueprint, Flask, jsonify

from flasgger import Swagger
from flasgger.utils import swag_from

app = Flask(__name__)

example_blueprint = Blueprint("example_blueprint", __name__)


@example_blueprint.route('/usernames/<username>', methods=['GET', 'POST'])
@swag_from('username_specs.yml', methods=['GET'])
@swag_from('username_specs.yml', methods=['POST'])
def usernames(username):
    return jsonify({'username': username})


@example_blueprint.route('/usernames2/<username>', methods=['GET', 'POST'])
def usernames2(username):
    """
    This is the summary defined in yaml file
    First line is the summary
    All following lines until the hyphens is added to description
    the format of the first lines until 3 hyphens will be not yaml compliant
    but everything below the 3 hyphens should be.
    ---
    tags:
      - users
    parameters:
      - in: path
        name: username
        type: string
        required: true
    responses:
      200:
        description: A single user item
        schema:
          id: rec_username
          properties:
            username:
              type: string
              description: The name of the user
              default: 'steve-harris'
    """
    return jsonify({'username': username})


app.register_blueprint(example_blueprint)

swag = Swagger(app)

if __name__ == "__main__":
    app.run(debug=True)

