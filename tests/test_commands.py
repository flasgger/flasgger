import json

from flask_openapi.base import Swagger
from flask_openapi.commands import generate_api_schema


def test_default_specs(app, cli_runner):
    swagger = Swagger(app)

    result = cli_runner.invoke(generate_api_schema)

    assert result.exit_code == 0
    spec = json.loads(result.output)
    assert spec == swagger.get_apispecs(Swagger.DEFAULT_ENDPOINT)


def test_custom_specs(app, cli_runner):
    endpoint = "custom_endpoint"
    config = dict(Swagger.DEFAULT_CONFIG)
    config["specs"][0]["endpoint"] = endpoint
    swagger = Swagger(app, config=config)

    result = cli_runner.invoke(generate_api_schema, ["-e", endpoint])

    assert result.exit_code == 0
    spec = json.loads(result.output)
    assert spec == swagger.get_apispecs(endpoint)


def test_invalid_endpoint(app, cli_runner):
    endpoint = "custom_endpoint"
    config = dict(Swagger.DEFAULT_CONFIG)
    config["specs"][0]["endpoint"] = endpoint
    Swagger(app, config=config)

    result = cli_runner.invoke(generate_api_schema, ["-e", "other_endpoint"])

    assert result.exit_code == 1
    assert "other_endpoint" in result.stderr


def test_definitions_is_removed_for_openapi_3(app, cli_runner):
    app.config["SWAGGER"] = {
        "openapi": "3.0.3",
    }

    Swagger(app)

    result = cli_runner.invoke(generate_api_schema)
    assert result.exit_code == 0
    assert "definitions" not in json.loads(result.output)
