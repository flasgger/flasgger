from flask import Blueprint, Flask, jsonify

from flasgger import Swagger
from flasgger.utils import swag_from


app = Flask(__name__)

example_blueprint = Blueprint("example_blueprint", __name__)


@example_blueprint.route('/usernames', methods=['GET', 'POST'])
@swag_from('username_specs.yml', methods=['GET'])
@swag_from('username_specs.yml', methods=['POST'])
def usernames(username):
    return jsonify({'username': username})


swag = Swagger(app, config={})

if __name__ == "__main__":
    app.run(debug=True)
