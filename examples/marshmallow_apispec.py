"""
Another example using Marshmallow schemas in SwaggerView (MethodView)
"""
# coding: utf-8

from flask import Flask, jsonify, request

from flasgger import Schema, Swagger, SwaggerView, fields

app = Flask(__name__)
app.config['SWAGGER'] = {
    "title": "API using Marshmallow",
    "uiversion": 2
}

swag = Swagger(app)


class User(Schema):
    username = fields.Str(required=True)
    age = fields.Int(required=True, min=18)
    tags = fields.List(fields.Str())


class UserPostView(SwaggerView):

    parameters = User

    # parameters = [
    #     {
    #         'name': 'body',
    #         'in': 'body',
    #         'schema': User
    #     }
    # ]

    responses = {
        200: {
            'description': 'A single user',
            'schema': User
        }
    }

    # optional
    # definitions = {
    #     'User': User  # if nto informed will be extracted from usage above
    # }
    tags = ['users']
    # consumes = ['application/json']
    # produces = ['application/json']
    # schemes = ['http', 'https']
    # security = []
    # deprecated = False
    # operationId = 'user'
    # externalDocs = {'description': 'foo', 'url': 'bar.com'}
    summary = "Will be overwritten by first line of docstring"
    description = "will be overwritten by otehr lines"

    def post(self):
        """
        A simple post
        Do it
        ---
        # This value overwrites the attributes above
        deprecated: true
        """
        return jsonify(request.json)


app.add_url_rule(
    '/user',
    view_func=UserPostView.as_view('user'),
    methods=['POST']
)

if __name__ == "__main__":
    app.run(debug=True)
