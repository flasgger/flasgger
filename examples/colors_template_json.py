"""
Example loading all specs from JSON template
"""
from flask import Flask, jsonify

from flasgger import Swagger

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Colors API',
    'uiversion': 2
}
swag = Swagger(app, template_file='colors_template.json')


@app.route('/colors/<palette>/')
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
