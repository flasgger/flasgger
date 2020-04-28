from flask import Flask
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


class Query(Schema):
    color = fields.String(required=True, validate=OneOf(["white", "blue", "red"]))
    swag_in = "query"


@app.route("/color/<id>/<name>", methods=["POST"], **swag)
def index(body: Body, query: Query, id: int, name: str):
    return {"body": Body, "query": query, "id": id, "name": name}


if __name__ == "__main__":
    app.run(debug=True)
