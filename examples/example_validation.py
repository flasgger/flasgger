from flask import Flask, jsonify, request

from flasgger import Swagger
from flasgger.utils import swag_from, validate

app = Flask(__name__)
Swagger(app)


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


app.run(debug=True)
