"""
Test the use of LazyString to populate a template at runtime.
"""

from flask import Flask, jsonify, request

from flasgger import Swagger, LazyString, LazyJSONEncoder

app = Flask(__name__)

# Set the LAzyString JSON Encoder
app.json_encoder = LazyJSONEncoder

app.config['SWAGGER'] = {
    'uiversion': 2
}

template = dict(
    info={
        'title': LazyString(lambda: 'Lazy Title'),
        'version': LazyString(lambda: '99.9.9'),
        'description': LazyString(lambda: 'Hello Lazy World'),
        'termsOfService': LazyString(lambda: '/there_is_no_tos')
    },
    host=LazyString(lambda: request.host),
    schemes=[LazyString(lambda: 'https' if request.is_secure else 'http')],
    foo=LazyString(lambda: "Bar")
)

Swagger(app, template=template)


@app.route('/colors/<palette>/')
def colors(palette):
    """Example endpoint return a list of colors by palette
    This is using docstring for specifications
    ---
    tags:
      - colors
    parameters:
      - name: palette
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
        required: true
        default: all
        description: Which palette to filter?
    operationId: get_colors
    consumes:
      - application/json
    produces:
      - application/json
    security:
      colors_auth:
        - 'write:colors'
        - 'read:colors'
    schemes: ['http', 'https']
    deprecated: false
    externalDocs:
      description: Project repository
      url: http://github.com/rochacbruno/flasgger
    definitions:
      Palette:
        type: object
        properties:
          palette_name:
            type: array
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          $ref: '#/definitions/Palette'
        examples:
          rgb: ['red', 'green', 'blue']
    """
    all_colors = {
        'cmyk': ['cian', 'magenta', 'yellow', 'black'],
        'rgb': ['red', 'green', 'blue']
    }
    if palette == 'all':
        result = all_colors
    else:
        result = {palette: all_colors.get(palette)}

    return jsonify(result)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    for url, spec in specs_data.items():
        assert 'Palette' in spec['definitions']
        assert 'Color' in spec['definitions']
        assert 'colors' in spec['paths']['/colors/{palette}/']['get']['tags']
        assert spec['schemes'] == ['http']
        assert spec['foo'] == 'Bar'


if __name__ == "__main__":
    app.run(debug=True)
