from unittest.mock import call

from flasgger.utils import LazyDict, CachedLazyDict
import pytest
from pytest_mock import mocker


def test_lazy_dict(mocker):

    stub = mocker.Mock(name='on_something_stub', return_value={"k": "v"})

    ld = LazyDict(stub)

    stub.assert_not_called()

    d = ld._get_dict()
    d = ld._get_dict()

    # Assert that func passed in LazyDict.__init__ is called twice
    stub.assert_has_calls([call(), call()])


def test_cached_dict(mocker):

    stub = mocker.Mock(name='on_something_stub', return_value={"k": "v"})

    ld = CachedLazyDict(stub)

    stub.assert_not_called()

    d = ld._get_dict()
    d = ld._get_dict()

    # Assert that func passed in LazyDict.__init__ is called once only
    stub.assert_called_once()

