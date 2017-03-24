from flask import Flask, jsonify, request

from flasgger import Swagger
from flasgger.utils import swag_from, validate

app = Flask(__name__)
Swagger(app)


@app.route("/", methods=['POST'])
@swag_from("test_validation.yml")
def index():
    data = request.json
    validate(data, 'user', "test_validation.yml")
    return jsonify(data)


app.run(debug=True)
