"""
A slight variation of the basic auth example to demonstrate using the
"decorators" parameter in init_app, instead of during Swagger object
creation itself.
This is useful in cases when the application factory pattern is used in your
flask app.
The example is very similar to the basic_auth example, except that the
decorators parameter is passed in init_app.
Doc for the original basic auth example follows.

An example that uses HTTP Basic Auth to protect the /apidocs and
/apispec_1.json endpoints.

In this example the login credentials to view the Swagger docs are as follows:

    Username: guest
    Password: secret

Failing to provide the right credentials results in a 401 Unauthorized
response from all the Flasgger endpoints.
"""
from flask import Flask, request, redirect, Response, jsonify
from functools import wraps

from flasgger import Swagger


def requires_basic_auth(f):
    """Decorator to require HTTP Basic Auth for your endpoint."""

    def check_auth(username, password):
        return username == "guest" and password == "secret"

    def authenticate():
        return Response(
            "Authentication required.", 401,
            {"WWW-Authenticate": "Basic realm='Login Required'"},
        )

    @wraps(f)
    def decorated(*args, **kwargs):
        # NOTE: This example will require Basic Auth only when you run the
        # app directly. For unit tests, we can't block it from getting the
        # Swagger specs so we just allow it to go thru without auth.
        # The following two lines of code wouldn't be needed in a normal
        # production environment.
        if __name__ != "__main__":
            return f(*args, **kwargs)

        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


app = Flask(__name__)
app.config["SWAGGER"] = {
    "title": "Swagger Basic Auth App",
    "uiversion": 2,
}
swag = Swagger(
    template={
        "swagger": "2.0",
        "info": {
            "title": "Swagger Basic Auth App",
            "version": "1.0",
        },
        "consumes": [
            "application/json",
        ],
        "produces": [
            "application/json",
        ],
    },
)
# passing decorators in init_app
swag.init_app(app, decorators=[requires_basic_auth])


@app.route("/echo/<name>", methods=["GET", "POST"])
def echo(name):
    """
    Echo back the name and any posted parameters.
    ---
    tags:
      - echo
    parameters:
      - in: path
        name: name
        type: string
        required: true
      - in: body
        name: body
        description: JSON parameters.
        schema:
          properties:
            first_name:
              type: string
              description: First name.
              example: Alice
            last_name:
              type: string
              description: Last name.
              example: Smith
            dob:
              type: string
              format: date
              description: Date of birth.
              example: 1990-01-01
            comment:
              type: string
              description: Something arbitrary.
              example: Hello world
    responses:
      200:
        description: OK.
    """
    data = {
        "url_name": name,
        "json": request.json,
    }
    return jsonify(data)


@app.route("/")
def index():
    return redirect("/apidocs")


if __name__ == "__main__":
    app.run(debug=True)
