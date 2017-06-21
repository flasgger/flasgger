"""
Example using marshmallow APISpec as base template for Flasgger specs
"""
# coding: utf-8
from flask import Flask, jsonify

from flasgger import APISpec, Schema, Swagger, fields

# Create an APISpec
spec = APISpec(
    title='Flasger Petstore',
    version='1.0.10',
    plugins=[
        'apispec.ext.flask',
        'apispec.ext.marshmallow',
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


template = spec.to_flasgger(
    app,
    definitions=[CategorySchema, PetSchema],
    paths=[random_pet]
)

"""
optionally if using apispec.APISpec from original module
you can do:

from flasgger.utils import apispec_to_template
template = apispec_to_template(
    app=app,
    spec=spec,
    definitions=[CategorySchema, PetSchema],
    paths=[random_pet]
)

"""

# start Flasgger using a template from apispec
swag = Swagger(app, template=template)


if __name__ == '__main__':
    app.run(debug=True)
