import time
import jsonschema
try:
    import simplejson as json
except ImportError:
    import json
try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus
from flask import Flask
from flask import jsonify
from flask import request
from flasgger import Swagger


def drop_id_validate(data, schema):
    """
    Custom validation function which drops parameter '_id' if present
    in data
    """
    jsonschema.validate(data, schema)
    if data.get('_id') is not None:
        del data['_id']


def timestamping_validate(data, schema):
    """
    Custom validation function which inserts a timestamp for when the
    validation occurred
    """
    jsonschema.validate(data, schema)
    data['timestamp'] = str(time.time())


def special_validate(data, schema):
    """
    Custom validation function which inserts an special flag depending
    on the cat's name
    """
    jsonschema.validate(data, schema)
    data['special'] = str(data['name'] == 'Garfield').lower()


def regular_validate(data, schema):
    """
    Regular validation function
    """
    jsonschema.validate(data, schema)


app = Flask(__name__)
swag = Swagger(app, validation_function=drop_id_validate)


@app.route('/cat', methods=['POST'])
@swag.validate('Cat')
def create_cat():
    """
    Cat creation endpoint which drops '_id' parameters when present in
    request data
    ---
    tags:
      - cat
    summary: Creates a new cat
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description:
          Cat object that needs to be persisted to the database
        required: true
        schema:
          id: Cat
          required:
            - name
            - address
          properties:
            name:
              description: Cat's name
              type: string
              example: Sylvester
            address:
              description: Cat's house address
              type: string
              example: 4000 Warner Blvd., Burbank, CA 91522
    responses:
      200:
        description: Successful operation
      400:
        description: Invalid input
    """
    return jsonify(request.json), HTTPStatus.OK


@app.route('/timestamped/cat', methods=['POST'])
@swag.validate('Cat', validation_function=timestamping_validate)
def create_timestamped_cat():
    """
    Cat creation endpoint which timestamps validated data
    ---
    tags:
      - cat
    summary: Creates a new cat
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description:
          Cat object that needs to be persisted to the database
        required: true
        schema:
          $ref: '#/definitions/Cat'
    responses:
      200:
        description: Successful operation
        schema:
          $ref: '#/definitions/Cat'
      400:
        description: Invalid input
    """
    return jsonify(request.json), HTTPStatus.OK


@app.route('/special/cat', methods=['POST'])
@swag.validate('Cat', validation_function=special_validate)
def create_special_cat():
    """
    Cat creation endpoint which timestamps validated data
    ---
    tags:
      - cat
    summary: Creates a new cat
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description:
          Cat object that needs to be persisted to the database
        required: true
        schema:
          $ref: '#/definitions/Cat'
    responses:
      200:
        description: Successful operation
        schema:
          $ref: '#/definitions/Cat'
      400:
        description: Invalid input
    """
    return jsonify(request.json), HTTPStatus.OK


@app.route('/regular/cat', methods=['POST'])
@swag.validate('Cat', validation_function=regular_validate)
def create_regular_cat():
    """
    Cat creation endpoint
    ---
    tags:
      - cat
    summary: Creates a new cat
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description:
          Cat object that needs to be persisted to the database
        required: true
        schema:
          $ref: '#/definitions/Cat'
    responses:
      200:
        description: Successful operation
        schema:
          $ref: '#/definitions/Cat'
      400:
        description: Invalid input
    """
    return jsonify(request.json), HTTPStatus.OK


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    cat = {
        '_id': "594dba7b2879334e411f3dcc",
        'name': "Tom",
        'address': "MGM, 245 N. Beverly Drive, Beverly Hills, CA 90210"
    }

    with client.post(
            '/cat', data=json.dumps(cat), content_type='application/json') as response:
        assert response.status_code == HTTPStatus.OK

        received = json.loads(response.data.decode('utf-8'))
        assert received.get('_id') is None
        assert received.get('timestamp') is None
        assert received.get('special') is None
        try:
            assert received.viewitems() < cat.viewitems()
        except AttributeError:
            assert received.items() < cat.items()

    with client.post(
            '/timestamped/cat', data=json.dumps(cat),
            content_type='application/json') as response:
        assert response.status_code == HTTPStatus.OK

        received = json.loads(response.data.decode('utf-8'))
        assert received.get('_id') == cat.get('_id')
        assert received.get('timestamp') is not None
        assert received.get('special') is None
        try:
            assert received.viewitems() > cat.viewitems()
        except AttributeError:
            assert received.items() > cat.items()

    with client.post(
            '/special/cat', data=json.dumps(cat),
            content_type='application/json') as response:
        assert response.status_code == HTTPStatus.OK

        received = json.loads(response.data.decode('utf-8'))
        assert received.get('_id') == cat.get('_id')
        assert received.get('timestamp') is None
        assert received.get('special') is not None
        try:
            assert received.viewitems() > cat.viewitems()
        except AttributeError:
            assert received.items() > cat.items()

    with client.post(
            '/regular/cat', data=json.dumps(cat),
            content_type='application/json') as response:
        assert response.status_code == HTTPStatus.OK

        received = json.loads(response.data.decode('utf-8'))
        assert received.get('_id') == cat.get('_id')
        assert received.get('timestamp') is None
        assert received.get('special') is None
        try:
            assert received.viewitems() == cat.viewitems()
        except AttributeError:
            assert received.items() == cat.items()

if __name__ == "__main__":
    app.run(debug=True)
