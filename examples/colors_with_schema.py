"""
Example using Marshmallow Schema and fields as definitions
"""
# coding: utf-8
from flask import Flask, jsonify

from flasgger import Schema, Swagger, SwaggerView, fields


class Color(Schema):
    name = fields.Str()


class Palette(Schema):
    pallete_name = fields.Str()
    colors = fields.Nested(Color, many=True)


class PaletteView(SwaggerView):
    parameters = [
        {
            "name": "palette",
            "in": "path",
            "type": "string",
            "enum": ["all", "rgb", "cmyk"],
            "required": True,
            "default": "all"
        }
    ]
    # definitions = {'Palette': Palette, 'Color': Color}
    responses = {
        200: {
            "description": "A list of colors (may be filtered by palette)",
            "schema": Palette
        }
    }

    def get(self, palette):
        """
        Colors API using schema
        This example is using marshmallow schemas
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


app = Flask(__name__)
swag = Swagger(app)

app.add_url_rule(
    '/colors/<palette>',
    view_func=PaletteView.as_view('colors'),
    methods=['GET']
)

if __name__ == "__main__":
    app.run(debug=True)
