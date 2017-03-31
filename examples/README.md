# Flasgger Examples

In this folder there is an example for each **Flasgger** functionality.

Each example on this folder represents a `test case` and is executed and validated when `make test` is executed.

This is the current testing running on `travis CI`

# Contributing

Please contribute adding your example to increase our test coverage

The only rules to follow is:

- Add extra requirements to `requirements.txt`
- use `if __name__ == '__main__':` before `app.run()`

# testing

You can also add extra tests to your example, just create a function called `test_swag` as:


```python
def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    for url, spec in specs_data.items():
        assert 'Palette' in spec['definitions']
        assert 'Color' in spec['definitions']
        # 'route '/colors/<palette>/' becomes '/colors/{palette}/'
        assert 'colors' in spec['paths']['/colors/{palette}/']['get']['tags']

```

