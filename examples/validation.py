"""
Example of JSON body validation in POST with various kinds of specs and views.
"""
try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus
from flask import Blueprint
from flask import Flask
from flask import jsonify
from flask import request
from flasgger import Schema
from flasgger import Swagger
from flasgger import SwaggerView
from flasgger import fields
from flasgger import swag_from
from flasgger import validate

app = Flask(__name__)
swag = Swagger(app)


test_specs_1 = {
  "tags": [
    "users"
  ],
  "parameters": [
    {
      "name": "body",
      "in": "body",
      "required": True,
      "schema": {
        "id": "User",
        "required": [
          "username",
          "age"
        ],
        "properties": {
          "username": {
            "type": "string",
            "description": "The user name.",
            "default": "Sirius Black"
          },
          "age": {
            "type": "integer",
            "description": "The user age (should be integer)",
            "default": "180"
          },
          "tags": {
            "type": "array",
            "description": "optional list of tags",
            "default": [
              "wizard",
              "hogwarts",
              "dead"
            ],
            "items": {
              "type": "string"
            }
          }
        }
      }
    }
  ],
  "responses": {
    "200": {
      "description": "A single user item",
      "schema": {
        "$ref": "#/definitions/User"
      }
    }
  }
}


@app.route("/manualvalidation", methods=['POST'])
@swag_from("test_validation.yml")
def manualvalidation():
    """
    In this example you need to call validate() manually
    passing received data, Definition (schema: id), specs filename
    """
    data = request.json
    validate(data, 'User', "test_validation.yml")
    return jsonify(data)


@app.route("/validateannotation", methods=['POST'])
@swag.validate('User')
@swag_from("test_validation.yml")
def validateannotation():
    """
    In this example you use validate(schema_id) annotation on the
    method in which you want to validate received data
    """
    data = request.json
    return jsonify(data)


@app.route("/autovalidation", methods=['POST'])
@swag_from("test_validation.yml", validation=True)
def autovalidation():
    """
    Example using auto validation from yaml file.
    In this example you don't need to call validate() because
    `validation=True` on @swag_from does that for you.
    In this case it will use the same provided filename
    and will extract the schema from `in: body` definition
    and the data will default to `request.json`

    or you can specify:
    @swag_from('file.yml',
               validation=True,
               definition='User',
               data=lambda: request.json,  # any callable
               )
    """
    data = request.json
    return jsonify(data)


@app.route("/autovalidationfromspecdict", methods=['POST'])
@swag_from(test_specs_1, validation=True)
def autovalidation_from_spec_dict():
    """
    Example using data from dict to validate.
    In this example you don't need to call validate() because
    `validation=True` on @swag_from does that for you.
    In this case it will use the same provided filename
    and will extract the schema from `in: body` definition
    and the data will default to `request.json`

    or you can specify:
    @swag_from('file.yml',
               validation=True,
               definition='User',
               data=lambda: request.json,  # any callable
               )
    """
    data = request.json
    return jsonify(data)


class User(Schema):
    username = fields.Str(required=True, default="Sirius Black")
    # wrong default "180" to force validation error
    age = fields.Int(required=True, min=18, default="180")
    tags = fields.List(fields.Str(), default=["wizard", "hogwarts", "dead"])


class UserPostView(SwaggerView):
    tags = ['users']
    parameters = User
    responses = {
        200: {
            'description': 'A single user item',
            'schema': User
        }
    }
    validation = True

    def post(self):
        """
        Example using marshmallow Schema
        validation=True forces validation of parameters in body
        ---
        # This value overwrites the attributes above
        deprecated: true
        """
        return jsonify(request.json)


app.add_url_rule(
    '/schemevalidation',
    view_func=UserPostView.as_view('schemevalidation'),
    methods=['POST']
)


# ensure the same works for blueprints

example_blueprint = Blueprint(
    "example", __name__, url_prefix='/blueprint')


@example_blueprint.route("/autovalidationfromdocstring", methods=['POST'])
@swag.validate('Officer')
def autovalidation_from_docstring():
    """
    Test validation using JsonSchema

    The default payload is invalid, try it, then change the age to a
    valid integer and try again
    ---
    tags:
      - officer
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: Officer
          required:
            - name
            - age
          properties:
            name:
              type: string
              description: The officer's name.
              default: "James T. Kirk"
            age:
              type: integer
              description: The officer's age (should be integer)
              default: "138"
            tags:
              type: array
              description: optional list of tags
              default: ["starfleet", "captain", "enterprise", "dead"]
              items:
                type: string

    responses:
      200:
        description: A single officer item
        schema:
          $ref: '#/definitions/Officer'
    """
    data = request.json
    return jsonify(data)


@example_blueprint.route('/manualvalidation', methods=['POST'])
@swag_from("test_validation.yml")
def manualvalidation_bp():
    """
    In this example you need to call validate() manually
    passing received data, Definition (schema: id), specs filename
    """
    data = request.json
    validate(data, 'User', "test_validation.yml")
    return jsonify(data)


@example_blueprint.route('/autovalidation', methods=['POST'])
@swag_from("test_validation.yml", validation=True)
def autovalidation_bp():
    """
    Example using auto validation from yaml file.
    In this example you don't need to call validate() because
    `validation=True` on @swag_from does that for you.
    In this case it will use the same provided filename
    and will extract the schema from `in: body` definition
    and the data will default to `request.json`

    or you can specify:
    @swag_from('file.yml',
               validation=True,
               definition='User',
               data=lambda: request.json,  # any callable
               )
    """
    data = request.json
    return jsonify(data)


@example_blueprint.route("/autovalidationfromspecdict", methods=['POST'])
@swag_from(test_specs_1, validation=True)
def autovalidation_from_spec_dict_bp():
    """
    Example using data from dict to validate.
    In this example you don't need to call validate() because
    `validation=True` on @swag_from does that for you.
    In this case it will use the same provided filename
    and will extract the schema from `in: body` definition
    and the data will default to `request.json`

    or you can specify:
    @swag_from('file.yml',
               validation=True,
               definition='User',
               data=lambda: request.json,  # any callable
               )
    """
    data = request.json
    return jsonify(data)


class BPUserPostView(SwaggerView):
    tags = ['users']
    parameters = User
    responses = {
        200: {
            'description': 'A single user item',
            'schema': User
        }
    }
    validation = True

    def post(self):
        """
        Example using marshmallow Schema
        validation=True forces validation of parameters in body
        ---
        # This value overwrites the attributes above
        deprecated: true
        """
        return jsonify(request.json)


example_blueprint.add_url_rule(
    '/schemevalidation',
    view_func=BPUserPostView.as_view('schemevalidation'),
    methods=['POST']
)


app.register_blueprint(example_blueprint)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """

    apispec = specs_data.get('/apispec_1.json')

    assert apispec is not None

    paths = apispec.get('paths')

    expected_user_paths = (
        '/autovalidation',
        '/validateannotation',
        '/autovalidationfromspecdict',
        '/blueprint/autovalidation',
        '/blueprint/autovalidationfromspecdict',
        '/blueprint/manualvalidation',
        '/blueprint/schemevalidation',
        '/manualvalidation',
        '/schemevalidation',
    )

    expected_officer_paths = (
        '/blueprint/autovalidationfromdocstring',
    )

    invalid_users = (
        """
        {
          "username": "Sirius Black",
          "age": "180",
          "tags": [
            "wizard",
            "hogwarts",
            "dead"
          ]
        }
        """,
        """
        {
          "age": 180,
          "tags": [
            "wizard"
          ]
        }
        """,
    )

    valid_users = (
        """
        {
          "username": "Sirius Black",
          "age": 180,
          "tags": [
            "wizard",
            "hogwarts",
            "dead"
          ]
        }
        """,
        """
        {
          "username": "Ronald Weasley",
          "age": 22
        }
        """,
    )

    invalid_officers = (
        """
        {
          "name": "James T. Kirk",
          "age": "138",
          "tags": [
            "captain",
            "enterprise",
            "dead"
          ]
        }
        """,
        """
        {
          "age": 138,
          "tags": [
            "captain"
          ]
        }
        """,
    )

    valid_officers = (
        """
        {
          "name": "James T. Kirk",
          "age": 138,
          "tags": [
            "captain",
            "enterprise",
            "dead"
          ]
        }
        """,
        """
        {
          "name": "Jean-Luc Picard",
          "age": 60
        }
        """,
    )

    assert paths is not None and len(paths) > 0

    definitions = apispec.get('definitions')

    assert definitions is not None
    assert definitions.get('User') is not None
    assert definitions.get('Officer') is not None

    for expected_path in expected_user_paths:
        assert paths.get(expected_path) is not None

        for invalid_user in invalid_users:
            response = client.post(
                expected_path, data=invalid_user,
                content_type='application/json')
            assert response.status_code == HTTPStatus.BAD_REQUEST

        for valid_user in valid_users:
            response = client.post(
                expected_path, data=valid_user,
                content_type='application/json')
            assert response.status_code == HTTPStatus.OK

    for expected_path in expected_officer_paths:
        assert paths.get(expected_path) is not None

        for invalid_officer in invalid_officers:
            response = client.post(
                expected_path, data=invalid_officer,
                content_type='application/json')
            assert response.status_code == HTTPStatus.BAD_REQUEST

        for valid_officer in valid_officers:
            response = client.post(
                expected_path, data=valid_officer,
                content_type='application/json')
            assert response.status_code == HTTPStatus.OK

if __name__ == "__main__":
    app.run(debug=True)
