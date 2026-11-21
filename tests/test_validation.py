from copy import deepcopy

import pytest
from flask import jsonify, request

from flasgger import swag_from, validate


@pytest.mark.parametrize("automatic", [False, True])
@pytest.mark.parametrize(
    "data, status, error",
    [
        ({"name": "example", "inherited": "value"}, 200, None),
        ({"name": "example"}, 400, "'inherited' is a required property"),
        ({"name": "example", "inherited": 42}, 400, "is not of type 'string'"),
    ],
)
def test_validate_allof_references(app, automatic, data, status, error):
    specs = {
        "parameters": [
            {
                "name": "body",
                "in": "body",
                "schema": {"$ref": "#/definitions/Item"},
            }
        ],
        "definitions": {
            "Base": {
                "type": "object",
                "properties": {"inherited": {"type": "string"}},
                "required": ["inherited"],
            },
            "Item": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
                "allOf": [{"$ref": "#/definitions/Base"}],
            },
        },
    }
    original_specs = deepcopy(specs)

    @app.route("/items", methods=["POST"])
    @swag_from(specs, validation=automatic)
    def items():
        if not automatic:
            validate(request.json, "Item", specs=specs)
        return jsonify(request.json)

    response = app.test_client().post("/items", json=data)

    assert response.status_code == status
    if error is None:
        assert response.get_json() == data
    else:
        assert error in response.get_data(as_text=True)
    assert specs == original_specs


@pytest.mark.parametrize("combinator", ["anyOf", "oneOf"])
def test_validate_composed_references(app, combinator):
    specs = {
        "definitions": {
            "Base": {"type": "integer", "minimum": 1},
            "Item": {combinator: [{"$ref": "#/definitions/Base"}]},
        }
    }

    @app.route("/items", methods=["POST"])
    def items():
        validate(request.json, "Item", specs=specs)
        return jsonify(request.json)

    client = app.test_client()
    assert client.post("/items", json=1).status_code == 200
    assert client.post("/items", json=-1).status_code == 400


def test_validate_nested_composed_file_references(app, tmp_path):
    base = tmp_path / "base.yaml"
    base.write_text("type: object\nrequired: [inherited]\n")
    schema = tmp_path / "schema.yaml"
    schema.write_text(
        "definitions:\n"
        "  Item:\n"
        "    allOf:\n"
        "      - anyOf:\n"
        "          - $ref: base.yaml\n"
    )

    @app.route("/items", methods=["POST"])
    def items():
        validate(request.json, "Item", filepath=str(schema))
        return jsonify(request.json)

    client = app.test_client()
    response = client.post("/items", json={"inherited": "value"})
    assert response.status_code == 200
    assert client.post("/items", json={"name": "example"}).status_code == 400


def test_validate_preserves_literal_reference_values(app):
    literal = {"$ref": "not-a-schema-file.yaml"}
    specs = {
        "definitions": {
            "Item": {
                "type": "object",
                "properties": {
                    "value": {"enum": [literal], "default": [literal]},
                },
            }
        }
    }

    @app.route("/items", methods=["POST"])
    def items():
        validate(request.json, "Item", specs=specs)
        return jsonify(request.json)

    data = {"value": literal}
    response = app.test_client().post("/items", json=data)
    assert response.status_code == 200
    assert response.get_json() == data
