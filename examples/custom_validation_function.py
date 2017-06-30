import jsonschema
try:
    import simplejson as json
except ImportError:
    import json
try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger


def validate(data, schema):
    """
    Custom validation function which drops parameter '_id' if present
    in data
    """
    jsonschema.validate(data, schema)
    if data.get('_id') is not None:
        del data['_id']


app = Flask(__name__)
swag = Swagger(app, validation_function=validate)


@app.route('/cat', methods=['POST'])
@swag.validate('Cat')
def create_cat():
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


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    cat = \
        """
        {
          "_id": "594dba7b2879334e411f3dcc",
          "name": "Tom",
          "address": "MGM, 245 N. Beverly Drive, Beverly Hills, CA 90210"
        }
        """
    response = client.post('/cat', data=cat, content_type='application/json')
    assert response.status_code == HTTPStatus.OK

    sent = json.loads(cat)
    received = json.loads(response.data.decode('utf-8'))
    assert received.get('_id') is None
    try:
        assert received.viewitems() < sent.viewitems()
    except AttributeError:
        assert received.items() < sent.items()

if __name__ == "__main__":
    app.run(debug=True)
