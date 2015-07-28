# flasgger
A Swagger 2.0 spec extractor for Flask

[![Code Health](https://landscape.io/github/rochacbruno/flasgger/master/landscape.svg?style=flat)](https://landscape.io/github/rochacbruno/flasgger/master)

[![wercker status](https://app.wercker.com/status/d86586341ba8b313162b36f84b192a9c/m "wercker status")](https://app.wercker.com/project/bykey/d86586341ba8b313162b36f84b192a9c)


# DEMO app

http://flasgger-rochacbruno.rhcloud.com/

**Powered by OpenShift**


# Install

```
pip install flasgger
```

# Configure 

> Take a look at flasgger/example_app.py

flasgger provides a method (swagger) that inspects the Flask app for endpoints that contain YAML docstrings with Swagger 2.0 [Operation](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#operation-object) objects.

```
class UserAPI(MethodView):

    def post(self):
        """
        Create a new user
        ---
        tags:
          - users
        parameters:
          - in: body
            name: body
            schema:
              id: User
              required:
                - email
                - name
              properties:
                email:
                  type: string
                  description: email for user
                name:
                  type: string
                  description: name for user
                address:
                  description: address for user
                  schema:
                    id: Address
                    properties:
                      street:
                        type: string
                      state:
                        type: string
                      country:
                        type: string
                      postalcode:
                        type: string
        responses:
          201:
            description: User created
        """
        return {}
```
flasgger supports docstrings in methods of MethodView classes (ala [Flask-RESTful](https://github.com/flask-restful/flask-restful)) and regular Flask view functions.

Following YAML conventions, flasgger searches for `---`, everything preceding is provided as `summary` (first line) and `description` (following lines) for the endpoint while everything after is parsed as a swagger [Operation](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#operation-object) object.

In order to support inline definition of [Schema ](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#schemaObject) objects in [Parameter](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#parameterObject)  and [Response](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#responsesObject) objects, flasgger veers a little off from the standard. We require an `id` field for the inline Schema which is then used to correctly place the [Schema](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#schemaObject) object in the [Definitions](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#definitionsObject) object.

[Schema ](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#schemaObject) objects can also be defined within the properties of other [Schema ](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#schemaObject) objects . An example is shown above with the address property of User.

To expose your Swagger specification to the world you provide a Flask route that does something along these lines

This is the DEMO app included in flasgger/example_app.py

```python
from flask import Flask, jsonify, request
from flask.views import MethodView
from flasgger import Swagger

app = Flask(__name__)


# config your API specs
# you can define multiple specs in the case your api has multiple versions
# ommit configs to get the default (all views exposed in /spec url)
# rule_filter is a callable that receives "Rule" object and
#   returns a boolean to filter in only desired views

app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    # headers are optional, the following are default
    # "headers": [
    #     ('Access-Control-Allow-Origin', '*'),
    #     ('Access-Control-Allow-Headers', "Authorization, Content-Type"),
    #     ('Access-Control-Expose-Headers', "Authorization"),
    #     ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
    #     ('Access-Control-Allow-Credentials', "true"),
    #     ('Access-Control-Max-Age', 60 * 60 * 24 * 20),
    # ],
    # another optional settings
    # "url_prefix": "swaggerdocs",
    # "subdomain": "docs.mysite,com",
    # specs are also optional if not set /spec is registered exposing all views
    "specs": [
        {
            "version": "0.0.1",
            "title": "Api v1",
            "endpoint": 'v1_spec',
            "route": '/v1/spec',

            # rule_filter is optional
            # it is a callable to filter the views to extract
            
            # "rule_filter": lambda rule: rule.endpoint.startswith(
            #    'should_be_v1_only'
            # )
        }
    ]
}

swagger = Swagger()  # you can pass config here Swagger(config={})


class UserAPI(MethodView):

    def get(self, team_id):
        """
        Get a list of users
        First line is the summary
        All following lines until the hyphens is added to description
        ---
        tags:
          - users
        parameters:
          - name: team_id
            in: path
            description: ID of team (type any number)
            required: true
            type: integer
        responses:
          200:
            description: Returns a list of users
            schema:
                type: array
                items:
                    $ref: '#/definitions/User'
        """
        data = {
            "users": [
                {"name": "Steven Wilson", "team": team_id},
                {"name": "Mikael Akerfeldt", "team": team_id},
                {"name": "Daniel Gildenlow", "team": team_id}
            ]
        }
        return jsonify(data)

    def post(self, team_id):
        """
        Create a new user
        First line is the summary
        All following lines until the hyphens is added to description
        ---
        tags:
          - users
        parameters:
          - name: team_id
            in: path
            description: ID of team (type any number)
            required: true
            type: integer
          - in: body
            name: body
            schema:
              id: User
              required:
                - team
                - name
              properties:
                team:
                  type: integer
                  description: team for user
                name:
                  type: string
                  description: name for user
        responses:
          201:
            description: User created
            schema:
                type: array
                items:
                    $ref: '#/definitions/User'
        """
        return jsonify({"newuser": request.json, "team_id": team_id})


view = UserAPI.as_view('users')
app.add_url_rule(
    '/v1/users/<int:team_id>',
    view_func=view,
    methods=["GET", "POST"],
    endpoint='should_be_v1_only_users'
)

# you can still use @app.route if you want

# initialize swagger
swagger.init_app(app)


if __name__ == "__main__":
    app.run(debug=True)

```


Acknowledgments

Flassger uses Swagger UI [Swagger-UI](https://github.com/swagger-api/swagger-ui)


Flasgger is a fork of [Flask-Swagger](https://github.com/gangverk/flask-swagger) which is a simpler solution, consider it if you just want to expose specs json.
