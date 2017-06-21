"""
Test compatibility with pre 0.5.14 version

- produces was accepted as string
- definitions references had method prefix
"""


from flask import Flask, jsonify, request

from flasgger import Swagger

app = Flask(__name__)
app.config['SWAGGER'] = {
    # set to True so instead of
    # $ref: '#/definitions/alert'
    # we get
    # $ref: '#/definitions/index_post_alert'
    'prefix_ids': True
}
swag = Swagger(app)


@app.route('/', methods=['POST'])
def index():
    """
    Test the compatibility
    This is just a test for flasgger 0.5.14 compat
    ---
    parameters:
      - in: body
        name: body
        schema:
          id: alert
          properties:
            message:
              type: string
    produces:
      application/json
    responses:
      200:
        description: Alert
        schema:
          $ref: '#/definitions/index_post_alert'
    """
    return jsonify({'message': request.json.get('message')})


if __name__ == '__main__':
    app.run(debug=True)
