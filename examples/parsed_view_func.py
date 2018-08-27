"""
Example of swagger document auto loading by endpoint
name(view function/method name), parsed by
flask_restful.reqparse.RequestParser and validated by jsonschema
"""
import os

from flask import Flask, request, jsonify, Response
from flask.views import MethodView
from flasgger import Swagger


app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Flasgger Parsed Method/Function View Example',
    'doc_dir': './examples/docs/'
}
swag = Swagger(
    app,
    template_file=os.path.join(
        os.getcwd(), 'examples', 'docs', 'template.yml'),
    parse=True)


class ItemsView(MethodView):
    """
    Flasgger will try to load "./examples/docs/items/{method}.yml" as
    swagger document
    """
    def get(self):
        """
        If we set "parse" is True in Flasgger app, we will get parsed and
        validated data stored in "flask.request.parsed_data".

        In "parsed_data", different location's var stored in different key,
        there is a map between RequestParser's location and swagger
        doc's "in" parameter, eg: 'query' -> 'args'.See
        "Swagger.SCHEMA_LOCATIONS" for more locations
        """
        return jsonify(
            [{'name': 'test', 'id': 1, 'type': request.parsed_data['args']['type']},
             {'name': 'test2', 'id': 2, 'type': request.parsed_data['args']['type']}])

    def post(self):
        return jsonify(
            {'name': request.parsed_data['json']['name'], 'id': 3,
             'type': request.parsed_data['json']['type']})


class ItemMethodView(MethodView):
    def get(self, id):
        return jsonify({'name': 'test', 'id': id, 'type': 'NORMAL'})

    def put(self, id):
        return jsonify(
            {'name': request.parsed_data['json']['name'], 'id': 3, 'type': 'NORMAL'})


class EmptyView(MethodView):
    """In this view, we do not provide api doc"""
    def get(self):
        return Response(status=200)


@app.route('/api/users/<group>/', methods=['POST'])
def users(group):
    """Create one user with nested json body.
    ---
    tags:
    - FunctionView
    parameters:
    - name: group
      in: path
      type: string
      required: true
    - name: User
      in: body
      schema:
        type: object
        required:
        - data
        properties:
          data:
             type: object
             required:
             - name
             - age
             properties:
                age:
                  type: integer
                name:
                  type: string
    definitions:
      User:
        type: object
        properties:
          id:
            type: integer
          name:
            type: string
          group:
            type: string
          age:
            type: integer
    responses:
      200:
        description: ok
        schema:
          $ref: '#/definitions/User'
        examples:
          {'id': 1, 'name': 'test', 'group': 1, 'age': 20}
      400:
        description: Miss data
    """
    return jsonify(
        {'id': 1,
         'name': request.parsed_data['json']['data']['name'],
         'age': request.parsed_data['json']['data']['age'],
         'group': request.parsed_data['path']['group']})


@app.route('/api/user/')
def user():
    """Flasgger will try to load './examples/docs/user.yml' as swagger doc
    """
    return jsonify({'id': request.parsed_data['args']['id'], 'name': 'test'})


app.add_url_rule(
    '/api/items/', view_func=ItemsView.as_view(name='items'),
    methods=['GET', 'POST'])
app.add_url_rule(
    '/api/items/<int:id>/', view_func=ItemMethodView.as_view(name='item'),
    methods=['GET', 'PUT'])
app.add_url_rule(
    '/api/empty/', view_func=EmptyView.as_view(name='empty'),
    methods=['GET'])


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    res = client.get('/api/items/')
    assert res.status_code == 400
    res = client.get('/api/items/?type=myLengthIsTooLong')
    assert res.status_code == 400
    res = client.get('/api/items/?type=NORMAL')

    assert res.status_code == 200
    res = client.get('/api/items/1/')
    assert res.status_code == 200
    res = client.put('/api/items/1/')
    assert res.status_code == 400
    res = client.put('/api/items/1/', json={'name': 'test'})
    assert res.status_code == 200

    res = client.post('/api/users/1/', json={'name': 'miss data'})
    assert res.status_code == 400
    res = client.post(
        '/api/users/1/',
        json={'data': {'name': 'test', 'age': 20}})
    assert res.status_code == 200


if __name__ == '__main__':
    app.run(debug=True)
