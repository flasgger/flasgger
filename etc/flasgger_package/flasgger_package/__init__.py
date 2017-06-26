from flask import jsonify
from flasgger import swag_from

@swag_from('package_specs.yml')
def package_view(username):
    return jsonify({'username': username})
