"""
Example using marshmallow APISpec as base template for Flasgger specs
"""
# coding: utf-8
from flask import Flask, jsonify

from flasgger import APISpec, Schema, Swagger, fields
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

# Create an APISpec
spec = APISpec(
    title='Flasger Petstore',
    version='1.0.10',
    openapi_version='2.0',
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)

app = Flask(__name__)


# Optional marshmallow support
class CategorySchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)


class PetSchema(Schema):
    category = fields.Nested(CategorySchema, many=True)
    name = fields.Str()


@app.route('/random')
def random_pet():
    """
    A cute furry animal endpoint.
    Get a random pet
    ---
    description: Get a random pet
    responses:
        200:
            description: A pet to be returned
            schema:
                $ref: '#/definitions/Pet'
    """
    pet = {'category': [{'id': 1, 'name': 'rodent'}], 'name': 'Mickey'}
    return jsonify(PetSchema().dump(pet).data)

@app.route("/add", methods=["POST"])
def create_pet(body: PetSchema) :
    """Create a cute furry animal endpoint.
    ---
    post:
      description: Create a random pet
      parameters: 
        - in: body
          name: body
          required: True
          schema:
                $ref: '#/definitions/Pet'
      security:
        - ApiKeyAuth: []
      responses:
        201:
          description: If pet is created
          content:
            application/json:
              status: string
    """
    return jsonify(
        {"status": "New user created"}
    ), 201


template = spec.to_flasgger(
    app,
    definitions=[CategorySchema, PetSchema],
    paths=[random_pet, create_pet]
)

"""
optionally if using apispec.APISpec from original module
you can do:

from flasgger.utils import apispec_to_template
template = apispec_to_template(
    app=app,
    spec=spec,
    definitions=[CategorySchema, PetSchema],
    paths=[random_pet, create_pet]
)

"""

# start Flasgger using a template from apispec
swag = Swagger(app, template=template)


if __name__ == '__main__':
    app.run(debug=True)
