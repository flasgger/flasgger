import pytest
from flasgger.base import Swagger


def test_init_config():

    class T(object):
        DEFAULT_CONFIG = Swagger.DEFAULT_CONFIG

    # Unspecified config will be initialized to dict()
    t = T()
    Swagger._init_config(self=t, config=None, merge=False)
    assert t.config == Swagger.DEFAULT_CONFIG

    # Empty dict passed to arguments will be overriden with default_config
    t = T()
    empty_dict = dict()
    Swagger._init_config(self=t, config=empty_dict, merge=False)
    assert t.config == Swagger.DEFAULT_CONFIG
    assert t.config is not empty_dict

    # Config will be merged
    t = T()
    d = {"a": 0}
    Swagger._init_config(self=t, config=d, merge=False)
    assert t.config is d

    # Config will be overridden
    t = T()
    Swagger._init_config(self=t, config={"a": 0}, merge=False)
    assert t.config == {"a": 0}

    # Config will be merged
    t = T()
    Swagger._init_config(self=t, config={"a": 0}, merge=True)
    assert t.config.items() > {"a": 0}.items()
    assert t.config.items() > Swagger.DEFAULT_CONFIG.items()

    # Config will be merged
    t = T()
    empty_dict = dict()
    Swagger._init_config(self=t, config=empty_dict, merge=True)
    assert t.config == Swagger.DEFAULT_CONFIG
