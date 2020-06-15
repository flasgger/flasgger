"""
Example using Marshmallow Schema and fields as definitions
"""
# coding: utf-8
from flask import Flask, jsonify, Response, request

from flasgger import Swagger, SwaggerView

swagger_config = {
    "headers": [],
    "openapi": "3.0.2",
    "components": {
        'schemas': {
            'Species': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer',
                        'format': 'int64'
                    },
                    'name': {
                        'type': 'string'
                    }
                }
            },
            'Animal': {
                'type': 'object',
                'properties': {
                    'species': {
                        '$ref': '#/components/schemas/Species'
                    },
                    'name': {
                        'type': 'string'
                    }
                }
            }
        }
    },
    "title": "Animal Shelter API",
    "version": '',
    "termsOfService": "",
    "static_url_path": "/characteristics/static",
    "swagger_ui": True,
    "description": "",
}


class Animals(SwaggerView):

    def get(self):
        """
        find shelter animals that fit the criteria

        ---
        tags:
        - Animals
        description: Parameters can be provided in the query to search
        operationId: getAnimals
        parameters:
            - name: species
              in: query
              required: true
              schema:
                type: string
            - name: status
              in: query
              required: true
              schema:
                type: string
                enum:
                  - adopted
                  - pending
                  - adoptable
                  - transferred
                  - sanctuary
                  - medical-hold
        responses:
            '200':
              description: Animals to be returned
              content:
                application/json:
                  schema:
                    type: array
                    items:
                      $ref: '#/components/schemas/Animal'
        """
        species = request.args.get('name')
        status = request.args.get('status')
        return Response(status=200)


app = Flask(__name__)
swag = Swagger(app, config=swagger_config, merge=True)

app.add_url_rule(
    '/animals',
    view_func=Animals.as_view('animals'),
    methods=['GET']
)

if __name__ == "__main__":
    app.run(debug=True)
