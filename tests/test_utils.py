from flask_openapi.utils import is_openapi3


def test_isopenapi_3_false():
    assert not is_openapi3(None)
    assert not is_openapi3("")
    assert not is_openapi3(5)
    assert not is_openapi3("2.0")
    assert not is_openapi3("1")


def test_isopenapi_3_true():
    assert is_openapi3("3")
    assert is_openapi3("3.3.3.3")
    assert is_openapi3(3)
    assert is_openapi3(3.0)
