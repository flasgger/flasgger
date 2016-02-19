from flask import Flask, jsonify, request
from flasgger import Swagger
from flasgger.utils import swag_from, validate, ValidationError
app = Flask(__name__)
Swagger(app)


@app.route("/", methods=['POST'])
@swag_from("test_validation.yml")
def index():
    data = request.json

    try:
        validate(data, 'user', "test_validation.yml", __file__)
    except ValidationError as e:
        return "Validation Error: %s" % e, 400

    return jsonify(data)

app.run(debug=True)
