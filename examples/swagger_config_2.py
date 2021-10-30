"""
In this example `openapi` version is used instead of `swagger` version.
"""
from flask import Flask, jsonify
from flasgger import Swagger, swag_from

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "swagger",
            "route": "/characteristics/swagger.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "title": "Product Characteristics APIs",
    "version": '',
    "termsOfService": "",
    "static_url_path": "/characteristics/static",
    "swagger_ui": True,
    "specs_route": "/characteristics/swagger/",
    "description": "",
    "securityDefinitions": {
        "oAuthSample": {
            "type": "oauth2",
            "flow": "application",
            "tokenUrl": "https://api.pgsmartshopassistant.com/o/token/",
        }
    }
}


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
    "colors_oauth": {
        "$ref": "#/securityDefinitions/oAuthSample"
    }
  },
  "schemes": [
    "http",
    "https"
  ],
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

swag = Swagger(app, config=swagger_config)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    for spec in specs_data.values():
        assert 'securityDefinitions' in spec
        assert 'oAuthSample' in spec['securityDefinitions']


if __name__ == '__main__':
    app.run(debug=True)
