import json
import random

from flasgger import Swagger
from flasgger.utils import get_examples


def get_specs_data(mod):
    """
    return all specs dictionary for some app
    """
    # for each example app in /examples folder
    client = mod.app.test_client()
    # init swag if not yet inititalized (no-routes example)
    if getattr(mod.app, 'swag', None) is None:
        _swag = Swagger()
        _swag.config['endpoint'] = str(random.randint(1, 5000))
        _swag.init_app(mod.app)
    # get all the specs defined for the example app
    apidocs = client.get('/apidocs/?json=true')
    specs = json.loads(apidocs.data.decode("utf-8")).get('specs')
    specs_data = {}
    for spec in specs:
        # for each spec get the spec url
        url = spec['url']
        response = client.get(url)
        decoded = response.data.decode("utf-8")
        specs_data[url] = json.loads(decoded)
    return specs_data


def pytest_generate_tests(metafunc):
    """
    parametrize tests using examples() function
    to generate one test for each examples/
    """
    test_data = [
        (mod, mod.app.test_client(), get_specs_data(mod))
        for mod in get_examples()
    ]

    metafunc.parametrize(
        'test_data',
        test_data,
        ids=lambda x: x[0].__name__
    )
