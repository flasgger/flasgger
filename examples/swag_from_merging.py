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
    },
    "tags": ["Tag 1", "Tag 2"]
})
def view():
    """
    A test view

    ---
    responses:
      200:
        description: OK
    tags: [Tag 3, Tag 4]
    """
    return jsonify(hello="world")


def test_swag(client, specs_data):
    example_spec = specs_data["/apispec_1.json"]["paths"]["/example"]["get"]
    assert "400" in example_spec["responses"]
    assert "401" in example_spec["responses"]
    assert "200" in example_spec["responses"]

    assert "Tag 1" in example_spec["tags"]
    assert "Tag 2" in example_spec["tags"]
    assert "Tag 3" in example_spec["tags"]
    assert "Tag 4" in example_spec["tags"]


if __name__ == "__main__":
    app.run(debug=True)
