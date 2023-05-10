from flask import Flask, abort
from flasgger import Swagger, Schema, fields
from marshmallow.validate import Length, OneOf

app = Flask(__name__)
Swagger(app)

swag = {"swag": True,
        "tags": ["demo"],
        "responses": {200: {"description": "Success request"},
                      400: {"description": "Validation error"}}}


class Body(Schema):
    color = fields.List(fields.String(), required=True, validate=Length(max=5), example=["white", "blue", "red"])

    def swag_validation_function(self, data, main_def):
        self.load(data)

    def swag_validation_error_handler(self, err, data, main_def):
        """
        NOTE: passing err (type of dict) to abort is supported only on flask>=1.1.0
        This will trigger an error on flask<1.1.0

        """
        abort(400, err)


class Query(Schema):
    color = fields.String(required=True, validate=OneOf(["white", "blue", "red"]))

    def swag_validation_function(self, data, main_def):
        self.load(data)

    def swag_validation_error_handler(self, err, data, main_def):
        abort(400, err)

    swag_in = "query"


# In this case: id is positive or nul
@app.route("/color/<id>/<name>", methods=["POST"], **swag)
def index(body: Body, query: Query, id: int, name: str):
    return {"body": body, "query": query, "id": id, "name": name}

# In this case: id is an integer
@app.route("/color2/<int(signed=True):id>/<name>", methods=["POST"], **swag)
def index2(body: Body, query: Query, id: int, name: str):
    return {"body": body, "query": query, "id": id, "name": name}

from flasgger import compatible
if compatible.flask_version >= compatible.v('1.1.0'):

    def test_swag(client, specs_data):
        """
        This test is runs automatically in Travis CI

        :param client: Flask app test client
        :param specs_data: {'url': {swag_specs}} for every spec in app
        """
        payload = {"color": ["white", "blue", "red"]}

        test_case = [
            {"url": '/color/100/putin?color=white', "status_code": 200},
            {"url": '/color/100/putin?color=black', "status_code": 400}
        ]
        for case in test_case:
            response = client.post(case["url"], json=payload)
            assert response.status_code == case["status_code"]
else:
    def test_swag(client, specs_data):
        """
        This test is runs automatically in Travis CI

        :param client: Flask app test client
        :param specs_data: {'url': {swag_specs}} for every spec in app
        """
        import logging
        logging.warning(f'test skipped for this flask version: {compatible.flask_version}')


if __name__ == "__main__":
    app.run(debug=True)
