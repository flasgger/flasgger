"""
The simple example using OpenAPI 3.0 callbacks
"""

from flask import Flask, jsonify

from flasgger import Swagger

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'OA3 Callbacks',
    'openapi': '3.0.2'
}
Swagger(app)


@app.route('/run_callback/',  methods=['POST'])
def run_callback():
    """Example endpoint that specifies OA3 callbacks
    This is using docstring for specifications
    ---
    tags:
      - callbacks
    requestBody:
      description: Test
      required: true
      content:
        application/json:
          schema:
            properties:
              callback_url:
                type: string
                format: uri
                description: Callback URL for request
    callbacks:
        onSomeEvent:
          '{$request.body.callback_url}':
            post:
              requestBody:
                description: status payload
                content:
                  application/json:
                    schema:
                      properties:
                        status:
                          type: string
    """

    return jsonify({'result': 'ok'})


def test_swag(client, specs_data):
    """
    This test is runs automatically in Travis CI

    :param client: Flask app test client
    :param specs_data: {'url': {swag_specs}} for every spec in app
    """
    for url, spec in specs_data.items():
        assert 'openapi' in spec
        assert spec['openapi'] == '3.0.2'

        assert 'callbacks' in spec['paths']['/run_callback/']['post']
        assert 'onSomeEvent' in \
               spec['paths']['/run_callback/']['post']['callbacks']


if __name__ == "__main__":
    app.run(debug=True)
