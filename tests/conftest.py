import json
import random

import pytest
from flasgger import Swagger
from flasgger.utils import get_examples

from flask import Flask


def get_specs_data(mod):
    """
    return all specs dictionary for some app
    """
    # for each example app in /examples folder
    from flask.testing import FlaskClient
    client: FlaskClient = mod.app.test_client()
    # init swag if not yet inititalized (no-routes example)
    specs_route = None
    specs_data = {}
    if getattr(mod.app, 'swag', None) is None:
        _swag = Swagger()
        _swag.config['endpoint'] = str(random.randint(1, 5000))
        _swag.init_app(mod.app)
    # get all the specs defined for the example app
    else:
        try:
            flasgger_config = mod.swag.config

            if flasgger_config.get('swagger_ui') is False:
                return specs_data

            specs_route = flasgger_config.get('specs_route', '/apidocs/')
        except AttributeError:
            pass

    if specs_route is None:
        specs_route = '/apidocs/'

    apidocs = client.get('?'.join((specs_route, 'json=true')))
    if 200 <= apidocs.status_code < 300:
        specs = json.loads(apidocs.data.decode("utf-8")).get('specs')

        for spec in specs:
            # for each spec get the spec url
            url = spec['url']
            response = client.get(url)
            decoded = response.data.decode("utf-8")
            if 200 <= response.status_code < 300:
                specs_data[url] = json.loads(decoded)
            else:
                raise ValueError(f'specs failure: {mod.__name__} {response.status}')
    else:
        raise ValueError(f'specs meta failure: {mod.__name__} {apidocs.status}')

    return specs_data


def get_test_metadata(mod):
    """Create a dictionary of test metadata defined in an example

    Every top-level constant prefixed with "_TEST_META_" is treated as
    metadata which may control test behavior. The prefix is stripped and the
    remaining text is lowercased to form the key in the metadata dictionary.

    Example: '_TEST_META_SKIP_FULL_VALIDATION' -> 'skip_full_validation'
    """

    test_metadata_prefix = '_TEST_META_'
    return {key[len(test_metadata_prefix):].lower(): getattr(mod, key)
            for key in mod.__dict__
            if key.startswith(test_metadata_prefix)}


def pytest_generate_tests(metafunc):
    """
    parametrize tests using examples() function
    to generate one test for each examples/
    """

    if 'test_data' in metafunc.fixturenames:
        test_data = [
            (mod, mod.app.test_client(),
             get_specs_data(mod), get_test_metadata(mod))
            for mod in get_examples()
        ]

        metafunc.parametrize(
            'test_data',
            test_data,
            ids=lambda x: x[0].__name__
        )


@pytest.fixture(scope="function")
def app():
    yield Flask(__name__)


@pytest.fixture(scope="function")
def cli_runner(app):
    yield app.test_cli_runner(mix_stderr=False)
