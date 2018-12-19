"""
The simple example using OpenAPI 3.0 callbacks
"""

from flask import Flask, jsonify

from flasgger import Swagger

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'OA3 Callbacks'
}
swagger_config = Swagger.DEFAULT_CONFIG
swagger_config['swagger_ui_bundle_js'] = '//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js'
swagger_config['swagger_ui_standalone_preset_js'] = '//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js'
swagger_config['jquery_js'] = '//unpkg.com/jquery@2.2.4/dist/jquery.min.js'
swagger_config['swagger_ui_css'] = '//unpkg.com/swagger-ui-dist@3/swagger-ui.css'
Swagger(app, config=swagger_config)

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
        assert 'callbacks' in spec['paths']['/run_callback/']['post']
        assert 'onSomeEvent' in spec['paths']['/run_callback/']['post']['callbacks']


if __name__ == "__main__":
    app.run(debug=True)
