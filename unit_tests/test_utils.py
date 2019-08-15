from flasgger.utils import LazyDict
import pytest
from pytest_mock import mocker


def test_lazy_dict(mocker):

    stub = mocker.stub(name='on_something_stub')

    ld = LazyDict(stub)

    stub.assert_not_called()

    d = ld._get_dict()
    d = ld._get_dict()

    stub.assert_called_once()
