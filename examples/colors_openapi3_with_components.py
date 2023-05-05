"""
The simple example using declared definitions with reusable components.
"""

from flask import Flask, jsonify

from flasgger import Swagger, utils

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Colors API',
    "openapi": "3.0.2",
}
Swagger(app)


@app.route('/colors/<palette>/')
def colors(palette):
    """Example endpoint return a list of colors by palette
    This is using docstring for specifications
    ---
    tags:
      - colors
    parameters:
      - $ref: "#/components/parameters/PaletteParameter"
    components:
      schemas:
        Palette:
          type: object
          properties:
            palette_name:
              type: array
              items:
                $ref: '#/components/schemas/Color'
        Color:
          type: string
      parameters:
        PaletteParameter:
          in: path
          type: string
          enum: ['all', 'rgb', 'cmyk']
          required: true
          default: all
          description: Which palette to filter?
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Palette'
            examples:
              rgb: ['red', 'green', 'blue']
    """
    all_colors = {
        'cmyk': ['cyan', 'magenta', 'yellow', 'black'],
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
        assert 'Palette' in spec['components']['schemas']
        assert 'Color' in spec['components']['schemas']
        assert 'PaletteParameter' in spec['components']['parameters']
        assert 'colors' in spec['paths']['/colors/{palette}/']['get']['tags']

if __name__ == "__main__":
    app.run(debug=True)
