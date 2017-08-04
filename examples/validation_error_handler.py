import jsonschema
from jsonschema import ValidationError
from werkzeug.exceptions import abort
from flask import Flask
try:
    from http import HTTPStatus
except ImportError:
    import httplib as HTTPStatus
try:
    import simplejson as json
except ImportError:
    import json
from flask import jsonify
from flask import Response
from flask import request
from flasgger import Swagger


def validation_error_inform_error(err, data, schema):
    """
    Custom validation error handler which produces 404 Bad Request
    response in case validation fails and returns the error
    """
    abort(Response(
        json.dumps({'error': str(err), 'data': data, 'schema': schema}),
        status=HTTPStatus.BAD_REQUEST))


def validation_error_404(err, data, schema):
    """
    Custom validation error handler which produces 404 Not Found
    response in case validation fails instead of 400 Bad Request
    """
    abort(Response(status=HTTPStatus.NOT_FOUND))


def validation_error_try_to_accept(err, data, schema):
    """
    Custom validation error handler which attempts alternative
    validation
    """
    if not isinstance(err, ValidationError):
        abort(Response(err, status=HTTPStatus.BAD_REQUEST))

    alernative_schema = dict(schema)
    alernative_schema['properties']['running_time'].update({
        'description': "Films's running time",
        'type': 'integer',
        'example': 169
    })

    try:
        jsonschema.validate(data, alernative_schema)
    except ValidationError as err:
        abort(Response(str(err), status=400))


app = Flask(__name__)
swag = Swagger(app, validation_error_handler=validation_error_inform_error)


@app.route('/film', methods=['POST'])
@swag.validate('Film')
def create_film():
    """
    Film creation endpoint
    ---
    tags:
      - film
    summary: Creates a new Film
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description:
          Film object that needs to be persisted to the database
        required: true
        schema:
          id: Film
          required:
            - title
            - director
            - distributor
            - release_date
            - running_time
          properties:
            title:
              description: Film's title
              type: string
              example: Interstellar
            director:
              description: Films's director
              type: string
              example: Christopher Nolan
            distributor:
              description: Films's distributor
              type: string
              example: Warner Bros. Pictures
            release_date:
              description: Films's release date
              type: string
              example: October 26, 2014
            running_time:
              description: Films's running time
              type: string
              example: 169 minutes
    responses:
      200:
        description: Successful operation
      400:
        description: Invalid input
    """
    return jsonify(request.json), HTTPStatus.OK


@app.route('/not_found/film', methods=['POST'])
@swag.validate('Film', validation_error_handler=validation_error_404)
def create_film_2():
    """
    Film creation endpoint
    ---
    tags:
      - film
    summary: Creates a new Film
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description:
          Film object that needs to be persisted to the database
        required: true
        schema:
          $ref: '#/definitions/Film'
    responses:
      200:
        description: Successful operation
      400:
        description: Invalid input
    """
    return jsonify(request.json), HTTPStatus.OK


@app.route('/retry/film', methods=['POST'])
@swag.validate('Film', validation_error_handler=validation_error_try_to_accept)
def create_film_3():
    """
    Film creation endpoint
    ---
    tags:
      - film
    summary: Creates a new Film
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description:
          Film object that needs to be persisted to the database
        required: true
        schema:
          $ref: '#/definitions/Film'
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
    invalid_film = {
        '_id': "594dba7b2879334e411f3dcc",
        'title': "The Last Airbender",
        'director': "M. Night Shyamalan",
        'distributor': "Paramount Pictures",
        'running_time': 103,
        'release_date': "June 30, 2010"
    }

    super_invalid_film = {
        'title': "The Last Airbender",
        'release_date': 2010
    }

    with client.post(
            '/film', data=json.dumps(invalid_film),
            content_type='application/json') as response:
        assert response.status_code == HTTPStatus.BAD_REQUEST

        received = json.loads(response.data.decode('utf-8'))
        assert received.get('error') is not None
        assert received.get('schema') is not None
        assert received.get('data') == invalid_film

    with client.post(
            '/not_found/film', data=json.dumps(invalid_film),
            content_type='application/json') as response:
        assert response.status_code == HTTPStatus.NOT_FOUND

    with client.post(
            '/retry/film', data=json.dumps(invalid_film),
            content_type='application/json') as response:
        assert response.status_code == HTTPStatus.OK

    with client.post(
            '/retry/film', data=json.dumps(super_invalid_film),
            content_type='application/json') as response:
        assert response.status_code == HTTPStatus.BAD_REQUEST

if __name__ == "__main__":
    app.run(debug=True)
