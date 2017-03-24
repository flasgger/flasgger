from flask import Flask, jsonify, request

from flasgger import Swagger
from flasgger.utils import swag_from, validate

app = Flask(__name__)
Swagger(app)


@app.route("/manualvalidation", methods=['POST'])
@swag_from("test_validation.yml")
def manualvalidation():
    """
    In this example you need to call validate() manually
    passing received data, Definition (schema: id), specs filename
    """
    data = request.json
    validate(data, 'User', "test_validation.yml")
    return jsonify(data)


@app.route("/autovalidation", methods=['POST'])
@swag_from("test_validation.yml", validation=True)
def autovalidation():
    """
    In this example you don't need to call validate() because
    `validation=True` on @swag_from does that for you.
    In this case it will use the same provided filename
    and will extract the schema from `in: body` definition
    and the data will default to `request.json`

    or you can specify:
    @swag_from('file.yml',
               validation=True,
               definition='User',
               data=lambda: request.json,  # any callable
               )
    """
    data = request.json
    return jsonify(data)


app.run(debug=True)
