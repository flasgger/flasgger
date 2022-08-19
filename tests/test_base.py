import pytest
from flask_openapi.base import Swagger


def test_init_config(monkeypatch):

    def __init__(self, config=None, merge=False):
        self._init_config(config, merge)

    monkeypatch.setattr(Swagger, "__init__", __init__)

    # # Unspecified config will be initialized to dict()
    t = Swagger(config=None, merge=False)
    assert t.config == Swagger.DEFAULT_CONFIG

    # Empty dict passed to arguments will be overriden with default_config
    empty_dict = dict()
    t = Swagger(config=empty_dict, merge=False)
    assert t.config == Swagger.DEFAULT_CONFIG
    assert t.config is not empty_dict

    # Config will be merged
    d = {"a": 0}
    t = Swagger(config=d, merge=False)
    assert t.config is d

    # Config will be overridden
    t = Swagger(config={"a": 0}, merge=False)
    assert t.config == {"a": 0}

    # Config will be merged
    t = Swagger(config={"a": 0}, merge=True)
    assert t.config.items() > {"a": 0}.items()
    assert all( t.config[k] == v for k, v in Swagger.DEFAULT_CONFIG.items() )

    # Config will be merged
    empty_dict = dict()
    t = Swagger(config=empty_dict, merge=True)
    assert t.config == Swagger.DEFAULT_CONFIG

    # keys in DEFAULT_CONFIG will be overridden
    d = {
        "specs": [
            {
                "endpoint": "swagger",
                "route": "/characteristics/swagger.json",
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
    }
    t = Swagger(config=d, merge=True)
    assert all(t.config[k] == v for k, v in d.items())
    assert t.config["specs"] == d["specs"]


def test_get_apispecs_with_invalid_endpoint(app):
    swagger = Swagger(app)

    with app.app_context():
        with pytest.raises(RuntimeError) as e:
            bad_endpoint = "Bad endpoint"
            swagger.get_apispecs(bad_endpoint)
            assert bad_endpoint in e


def test_get_apispecs_with_valid_endpoint(app):
    swagger = Swagger(app)

    with app.app_context():
        assert swagger.get_apispecs(Swagger.DEFAULT_ENDPOINT)
