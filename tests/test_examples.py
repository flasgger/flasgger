import json

import random
from flasgger import Swagger
from flex.core import validate


def test_validate_example_specs(examples):
    for example in examples:
        # for each example app in /examples folder
        app = example.app.test_client()
        # init swag if not yet inititalized (no-routes example)
        if getattr(example.app, 'swag', None) is None:
            _swag = Swagger()
            _swag.config['endpoint'] = str(random.randint(1, 5000))
            _swag.init_app(example.app)
        # get all the specs defined for the example app
        apidocs = app.get('/apidocs/?json=true')
        specs = json.loads(apidocs.data.decode("utf-8")).get('specs')
        for spec in specs:
            # for each spec get the spec url
            url = spec['url']
            response = app.get(url)
            decoded = response.data.decode("utf-8")
            assert 'paths' in decoded, 'paths is required'
            assert 'info' in decoded, 'info is required'
            result = json.loads(decoded)
            # validate using Flex
            validate(result)
