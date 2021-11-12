"""
In this example `openapi` version is used instead of `swagger` version.
"""
from flask import Flask
from flasgger import Swagger

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "openapi": "3.0.2",
    "components": {
        "securitySchemes": {
            "oAuthSample": {
                "type": "oauth2",
                "flows": {
                    "clientCredentials": {
                        "tokenUrl": "https://api.pgsmartshopassistant.com/o/token/",
                    }
                }
            }
        },
    },
    "servers": [
        {
            "url": "https://api.example.com/v1",
            "description": "Production server (uses live data)"
        },
        {
            "url": "https://sandbox-api.example.com:8443/v1",
            "description": "Sandbox server (uses test data)"
        }
    ],
    "specs": [
        {
            "endpoint": "swagger",
            "route": "/characteristics/swagger.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "title": "Product Characteristics API",
    "version": '',
    "termsOfService": "",
    "static_url_path": "/characteristics/static",
    "swagger_ui": True,
    "specs_route": "/characteristics/swagger/",
    "description": "",
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
  "components":{
    "schemas":{
      "Palette": {
        "type": "object",
        "properties": {
          "palette_name": {
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/Color"
            }
          }
        }
      },
      "Color": {
        "type": "string"
      }
    }
  },
  "responses": {
    "200": {
      "description": "A list of colors (may be filtered by palette)",
      "schema": {
        "$ref": "#/components/schemas/Palette"
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


swag = Swagger(app, config=swagger_config)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    for spec in specs_data.values():
        assert 'openapi' in spec
        assert '3.0.2' == spec['openapi']
        assert 'swagger' not in spec
        assert 'components' in spec
        assert 'securitySchemes' in spec['components']
        assert 'oAuthSample' in spec['components']['securitySchemes']

        assert 'servers' in spec  # See issue #366


if __name__ == '__main__':
    app.run(debug=True)
