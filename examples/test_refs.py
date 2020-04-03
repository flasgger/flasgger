# -*- coding: utf-8 -*-

"""
Example to test cascading $refs and basePath
"""

from flask import Flask, jsonify, Blueprint
from flasgger import swag_from, Swagger
try:
    import simplejson as json
except ImportError:
    import json

try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus


swagger_description = 'test_refs_basePath_API.yaml'

app = Flask(__name__)

swagger = Swagger(app, template_file=swagger_description)

api_blueprint = Blueprint('api', 'api', url_prefix='/api')


@api_blueprint.route('/get_cost', methods=['POST'])
@swag_from(swagger.template, definition='GetCostRequest', validation=True)
def get_cost():
    result = dict(description='The best place',
                  cost=dict(currency='EUR', value=123456))
    return jsonify([result])


app.register_blueprint(api_blueprint)


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """

    with client.get('apispec_1.json') as response:
        assert response.status_code == HTTPStatus.OK

        response_data = json.loads(response.data)

        assert response_data.get('basePath') == '/api/', \
            'wrong basePath: %r' % response_data

        paths = response_data.get('paths')
        assert '/get_cost' in paths, \
            'get_cost NOK: %r' % response_data
        assert '/api/get_costs' not in paths, \
            '/api/get_cost NOK: %r' % response_data

    req_data = dict(level=2,
                    location=dict(name='my preferred location',
                                  position=dict(latitude=47.352735,
                                                longitude=0.593682)))

    with client.post('/api/get_cost', data=json.dumps(req_data),
                     content_type='application/json') as response:
        assert response.status_code == HTTPStatus.OK, \
            'bad status: %r' % response.data


if __name__ == '__main__':
    app.run(debug=True)
