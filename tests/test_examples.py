import json

from flex.core import validate

# allow for different spec routes in examples
spec_urls = [
    "/apispec_1.json",
    "/v1/spec",
]


def test_validate_example_specs(examples):
    for example in examples:
        app = example.app.test_client()
        responses = [app.get(url) for url in spec_urls]
        response = next(filter(lambda r: r.status_code == 200, responses))
        decoded = response.data.decode("utf-8")
        spec = json.loads(decoded)
        validate(spec)
