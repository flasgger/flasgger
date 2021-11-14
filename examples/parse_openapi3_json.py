"""
In this example `openapi` version is used instead of `swagger` version.
This example will test validation when post
"""
from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)
swag = Swagger(app, template_file='parse_openapi3_json_product_schema.yml',
    parse=True, config={
    'headers': [],
    'specs': [
        {
            'endpoint': 'apispec',
            'route': '/apispec.json',
            'test': 'test'
        }
    ],
    'openapi': '3.0.1'
})

class NewProduct(Resource):
    def post(self):
        pass

api.add_resource(NewProduct, '/product')

def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    
    res = client.post('product', json={'id': 0, 'upc': 1})
    assert res.status_code == 200

    res = client.post('product', json={'id': 0, 'upc': 'astring'})
    assert res.status_code == 400

if __name__ == '__main__':
    app.run(debug=True)
