from flask import Flask, jsonify

from flasgger import Swagger

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Colors API',
    'uiversion': 2
}
Swagger(app)


@app.route('/colors/<palette>/')
def colors(palette):
    """Example endpoint return a list of colors by palette
    ---
    parameters:
      - name: palette
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
        required: true
        default: all
        description: Which palette to filter?
    definitions:
      - Palette:
          type: object
          properties:
            palette_name:
              type: array
              items:
                $ref: '#/definitions/Color'
      - Color:
          type: string
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          $ref: '#/definitions/Palette'
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


if __name__ == "__main__":
    app.run(debug=True)
