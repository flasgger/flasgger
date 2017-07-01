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
from flasgger import Swagger
from flasgger import swag_from

app = Flask(__name__)
swag = Swagger(app)


@app.route("/officer/<int:priority>", methods=['POST'])
@swag_from("officer_specs.yml")
def create_officer(priority):
    return 'Request for officer creation successfully received' \
           ' (priority: %i)'.format(priority), HTTPStatus.OK


@app.route('/schema/<string:schema_id>', methods=['GET'])
def get_schema(schema_id):
    """
    Test schema retrieval

    This endpoint returns a schema known to Flasgger
    ---
    tags:
      - schema
    produces:
      - application/json
    parameters:
      - in: path
        name: schema_id
        type: string
        description: schema_id to be retrieved
        required: true

    responses:
      200:
        description: The requested schema
    """
    return jsonify(swag.get_schema(schema_id)), HTTPStatus.OK


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    response = client.get('/schema/officer')
    assert response.status_code == HTTPStatus.OK

    retrieved_schema = json.loads(response.data.decode('utf-8'))
    actual_schema = specs_data['/apispec_1.json']['definitions']['Officer']
    try:
        assert retrieved_schema.viewitems() >= actual_schema.viewitems()
    except AttributeError:
        assert retrieved_schema.items() >= actual_schema.items()

if __name__ == "__main__":
    app.run(debug=True)
