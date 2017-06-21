"""
Example using a dictionary as specification instead of YAML
"""
from flask import Flask, jsonify

from flasgger import Swagger
from flasgger.utils import swag_from

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Colors API',
    'uiversion': 2
}
swag = Swagger(app)


colors_spec = {
  "tags": [
    "colors"
  ],
  "parameters": [
    {
      "name": "palette",
      "in": "path",
      "type": "string",
      "enum": [
        "all",
        "rgb",
        "cmyk"
      ],
      "required": True,
      "default": "all",
      "description": "Which palette to filter?"
    }
  ],
  "operationId": "get_colors",
  "consumes": [
    "application/json"
  ],
  "produces": [
    "application/json"
  ],
  "security": {
    "colors_auth": [
      "write:colors",
      "read:colors"
    ]
  },
  "schemes": [
    "http",
    "https"
  ],
  "deprecated": False,
  "externalDocs": {
    "description": "Project repository",
    "url": "http://github.com/rochacbruno/flasgger"
  },
  "definitions": {
    "Palette": {
      "type": "object",
      "properties": {
        "palette_name": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/Color"
          }
        }
      }
    },
    "Color": {
      "type": "string"
    }
  },
  "responses": {
    "200": {
      "description": "A list of colors (may be filtered by palette)",
      "schema": {
        "$ref": "#/definitions/Palette"
      },
      "examples": {
        "rgb": [
          "red",
          "green",
          "blue"
        ]
      }
    }
  }
}


@app.route('/colors/<palette>/')
@swag_from(colors_spec)
def colors(palette):
    """
    Example using a dictionary as specification
    This is the description
    You can also set 'summary' and 'description' in
    specs_dict
    ---
    # values here overrides the specs dict
    deprecated: true
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
