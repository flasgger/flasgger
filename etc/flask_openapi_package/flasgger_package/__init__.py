from flask import jsonify
from flask_openapi import swag_from

@swag_from('package_specs.yml')
def package_view(username):
    return jsonify({'username': username})
