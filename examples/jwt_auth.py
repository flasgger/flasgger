"""
This example demonstrates usage of JWT token authentication with
Flasgger-enabled application.

Swagger version used is 3, although 2 will also run just fine. For more details
on how to use Flask-JWT in general, take a look at the:
https://pythonhosted.org/Flask-JWT.

In this example the login credentials to call the protected API are as follows:

    Username: guest
    Password: secret

In order to access protected API methods, user must first login with valid
credentials. Successful login appends JWT token in login response header
(name of the field is: jwt-token) - this is the field that Swagger-UI will
search for when gets the response and if found - it will be automatically use
its value when issuing next requests. These requests have Authorization HTTP
header field with content set to: JWT token_value_goes_here (note the space
between JWT and token value).

Benefit of this solution is that once token is obtained, there is no need to
enter it manually while working. Consider a good practice to implement method
to refresh token, in order to prevent token expiration.

Note however that if you want to use JWT_AUTH_HEADER_NAME - you must provide
your own JWT request handler. This is because flask-jwt is not actively
maintained anymore, making it impossible to add JWT_AUTH_HEADER_NAME to it. In
normal circumstances, you will not need to use this field, but if you want to
protect your Flasgger page in order to prevent unauthorized access to it by
using basic HTTP auth on some web-server you will have to.
"""


from flask import Flask, jsonify, request
from flask_jwt import JWT, jwt_required, current_identity, JWTError
from werkzeug.security import safe_str_cmp
from flasgger import Swagger


class User(object):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id


users = [
    User(1, 'guest', 'secret'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "super-secret"
app.config["SWAGGER"] = {
    "title": "Swagger JWT Authentiation App",
    "uiversion": 3,
}
app.config['JWT_AUTH_URL_RULE'] = '/api/auth'
app.config['JWT_AUTH_HEADER_NAME'] = 'JWTAuthorization'

swag = Swagger(app,
    template={
        "openapi": "3.0.0",
        "info": {
            "title": "Swagger Basic Auth App",
            "version": "1.0",
        },
        "consumes": [
            "application/x-www-form-urlencoded",
        ],
        "produces": [
            "application/json",
        ],
    },
)


def jwt_request_handler():
    auth_header_name = app.config['JWT_AUTH_HEADER_NAME']
    auth_header_value = request.headers.get(auth_header_name, None)
    auth_header_prefix = app.config['JWT_AUTH_HEADER_PREFIX']

    if not auth_header_value:
        return

    parts = auth_header_value.split()

    if parts[0].lower() != auth_header_prefix.lower():
        raise JWTError('Invalid JWT header', 'Unsupported authorization type')
    elif len(parts) == 1:
        raise JWTError('Invalid JWT header', 'Token missing')
    elif len(parts) > 2:
        raise JWTError('Invalid JWT header', 'Token contains spaces')

    return parts[1]


jwt = JWT(app, authenticate, identity)
jwt.request_handler(jwt_request_handler)


@app.route("/login", methods=["POST"])
def login():
    """
    User authenticate method.
    ---
    description: Authenticate user with supplied credentials.
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: User successfully logged in.
      400:
        description: User login failed.
    """
    try:
        username = request.form.get("username")
        password = request.form.get("password")

        user = authenticate(username, password)
        if not user:
            raise Exception("User not found!")

        resp = jsonify({"message": "User authenticated"})
        resp.status_code = 200

        access_token = jwt.jwt_encode_callback(user)

        # add token to response headers - so SwaggerUI can use it
        resp.headers.extend({'jwt-token': access_token})

    except Exception as e:
        resp = jsonify({"message": "Bad username and/or password"})
        resp.status_code = 401

    return resp


@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    """
    Protected content method.
    ---
    description: Protected content method. Can not be seen without valid token.
    responses:
      200:
        description: User successfully accessed the content.
    """
    resp = jsonify({"protected": "{} - you saw me!".format(current_identity)})
    resp.status_code = 200

    return resp


if __name__ == '__main__':
    app.run()
