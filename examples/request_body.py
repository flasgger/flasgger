"""
In this example `openapi` version is used instead of `swagger` version.
"""
from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from

app = Flask(__name__)
swag = Swagger(app, config={
    'headers': [],
    'specs': [
        {
            'endpoint': 'apispec',
            'route': '/apispec.json'
        }
    ],
    'openapi': '3.0.1'
})


@swag.definition('Pet')
class Pet(object):
    """
    Pet Object
    ---
    properties:
        name:
            type: string
    """
    def __init__(self, name):
        self.name = str(name)

    def dump(self):
        return dict(vars(self).items())


@app.route('/requestBody', methods=['POST'])
@swag_from()
def request_body_endpoint():
    """
    An endpoint for testing requestBody documentation.
    ---
    description: Post a request body
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/definitions/Pet'
        required: true
    responses:
        200:
            description: The posted request body
            content:
                application/json:
                    schema:
                        $ref: '#/definitions/Pet'
    """
    return jsonify(request.json)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    for url, spec in specs_data.items():
        assert 'Pet' in spec['definitions']

        assert 'paths' in spec
        paths = spec['paths']
        for path_def in paths.values():
            for method_def in path_def.values():
                assert 'requestBody' in method_def


if __name__ == '__main__':
    app.run(debug=True)
