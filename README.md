# flasgger
A Swagger 2.0 spec extractor for Flask

[![Code Health](https://landscape.io/github/rochacbruno/flasgger/master/landscape.svg?style=flat)](https://landscape.io/github/rochacbruno/flasgger/master)

[![wercker status](https://app.wercker.com/status/d86586341ba8b313162b36f84b192a9c/m "wercker status")](https://app.wercker.com/project/bykey/d86586341ba8b313162b36f84b192a9c)


Install:
```
pip install flasgger
```

> Take a look at examples/example.py

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

```
from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)

app.config['SWAGGER'] = {
    "version": "0.0.1",
    "title": "Example site title",
    "specs": [
        {
            "endpoint": 'v1_spec',
            "route": '/v1/spec',
            "rule_filter": lambda rule: True
        },
    ]
}

# you can pass many specs registers and use rule_filter to 
# separate versions

swagger = Swagger()  # you can pass config here if prefered

# register your views and blueprints and then

swagger.init_app(app)


if __name__ == "__main__":
    app.run(debug=True)

```

If you need to add some aditional info 
```
app.config['SWAGGER'] = {
    "version": "0.0.1",
    "title": "Example site title",
    "specs": [
        {
            "endpoint": 'v1_spec',
            "route": '/v1/spec',
            "rule_filter": lambda rule: True
            "extra_data": {
                "info": {"version": "0.1.2"},
                "foo": "bar"
            }
        },
    ]
}
```


[Swagger-UI](https://github.com/swagger-api/swagger-ui)

Swagger-UI is the reason we embarked on this mission to begin with, flasgger does not however include Swagger-UI. Simply follow the awesome documentation over at https://github.com/swagger-api/swagger-ui and point your [swaggerUi.url](https://github.com/swagger-api/swagger-ui#swaggerui) to your new flasgger endpoint and enjoy.


Acknowledgments

Flasgger is a fork of Flask-Swagger that builds on ideas and code from [flask-sillywalk](https://github.com/hobbeswalsh/flask-sillywalk) and [flask-restful-swagger](https://github.com/rantav/flask-restful-swagger)
