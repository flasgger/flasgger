from flask import Flask
from flask import jsonify
from flasgger import Swagger
from flasgger import swag_from

app = Flask(__name__)
swag = Swagger(app)


@app.route("/example")
@swag_from({
    "responses": {
        400: {
            "description": "Invalid action"
        },
        401: {
            "description": "Login required"
        }
    }
})
def view():
    """
    A test view

    ---
    responses:
      200:
        description: OK
      400:
        description: Modified description
    """
    return jsonify(hello="world")


def test_swag(client, specs_data):
    example_spec = specs_data["/apispec_1.json"]["paths"]["/example"]["get"]
    assert "400" in example_spec["responses"]
    assert "401" in example_spec["responses"]
    assert "200" in example_spec["responses"]

    assert example_spec["responses"]["400"]["description"] == "Modified description"


if __name__ == "__main__":
    app.run(debug=True)
