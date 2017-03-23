# flasgger
Creates Swagger 2.0 API documentation for all your Flask views extracting specs from docstrings or referenced YAML files.

The Swagger UI is embedded and docs by default available in **/apidocs/index.html**

[![Code Health](https://landscape.io/github/rochacbruno/flasgger/master/landscape.svg?style=flat)](https://landscape.io/github/rochacbruno/flasgger/master)

<a target="_blank" href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&amp;business=rochacbruno%40gmail%2ecom&amp;lc=BR&amp;item_name=Flasgger&amp;no_note=0&amp;currency_code=USD&amp;bn=PP%2dDonationsBF%3abtn_donate_SM%2egif%3aNonHostedGuest"><img alt='Donate with Paypal' src='http://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif' /></a>

flasgger provides an extension (Swagger) that inspects the Flask app for endpoints that contain YAML docstrings with Swagger 2.0 [Operation](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#operation-object) objects.

# DEMO app

http://flasgger-rochacbruno.rhcloud.com/

**Powered by OpenShift**


# Getting started

## create a virtualenv

```
mkvirtualenv test_api

# or

virtualenv test_api

#or

pyenv test_api
```

## install
```
pip install flasgger
```

or (dev version)

```
pip install https://github.com/rochacbruno/flasgger/tarball/master 
```

Create a file called for example `colors.py`

```python
from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)

@app.route('/colors/<pallete>/')
def colors(pallete):
    """Example endpoint return a list of colors by group
    ---
    parameters:
      - name: pallete
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
    responses:
      200:
        description: A list of colors (may be filtered by pallete)
        schema:
          id: colors
          properties:
            colors:
              type: array
              items:
                type: string
    """
    all_colors = {
        'cmyk': ['cian', 'magenta', 'yellow', 'black'],
        'rgb': ['red', 'green', 'blue']
    }
    return jsonify(
      colors=all_colors if pallete == 'all' else all_colors.get(pallete)
    )


if __name__ == "__main__":
    app.run(debug=True)
```

Now run:  

```
python colors.py
```

Access in your browser: [http://localhost:5000/apidocs/index.html](http://localhost:5000/apidocs/index.html)

You should get:

![colors](docs/colors.png)




## Definitions

```python
from flask import Flask, jsonify, request
from flasgger import Swagger
from flask.views import View

app = Flask(__name__)

# Flasgger is initialized like a standard flask extension.
# You can also use .init_app() with the "app factory" pattern.
swag = Swagger(app)


# Definitions can be registered as objects or functions.
# Docstring lines (before '---') are used as the description.
# YAML after '---' defines the Swagger definition schema.
@swag.definition('return_test_1')
class ReturnTest(object):
    """
    test return
    ---
    properties:
      result:
        type: string
        description: The test
        default: 'test1'
    """

    def __init__(self, size):
        self.size = int(size)

    def dump(self):
        return {"result": "test1" * self.size}


@swag.definition('return_test_2')
def return_test(size):
    """
    another test return
    ---
    properties:
      result:
        type: string
        description: The test
        default: 'test2'
    """
    size = int(size)

    return {"result": "test2" * size}


# Flask endpoints with flasgger docstrings are automatically registered.
# The first line of the docstring is used as the summary.
# The following lines (before '---') are used as the description.
# YAML after '---' defines the Swagger path schema.
@app.route("/recs", methods=['GET'])
def recs():
    """
    A simple test API
    This endpoint does nothing
    Only returns "test"
    ---
    tags:
      - testapi
    parameters:
      - name: size
        in: query
        type: string
        description: size of elements
    responses:
      200:
        description: A single user item
        schema:
          $ref: '#/definitions/return_test_1'
    """
    message = ReturnTest(request.args.get('size', 1)).dump()
    return jsonify(message)


class Foo(View):
    methods = ['GET', 'POST']

    def dispatch_request(self):
        """
        A simple test API
        This endpoint does nothing
        Only returns "test"
        ---
        tags:
          - rohit
        parameters:
          - name: size
            in: query
            type: string
            description: size of elements
        responses:
          200:
            description: A single user item
            schema:
              $ref: '#/definitions/return_test_2'
        """
        message = return_test(request.args.get('size', 1))
        return jsonify(message)


app.add_url_rule('/dispatch_request', view_func=Foo.as_view('foo'))
app.run(debug=True)
```
##  run

```python
python simple_test.py
```

## try

- http://localhost:5000/apidocs/index.html

# Install

```
pip install flasgger
```

# Run demo app

```
python -m flasgger.example_app
```

Access: http://localhost:5000 to see the demo app running

## you can run in gunicorn

```
pip install gunicorn

gunicorn flasgger.example_app:app -b 0.0.0.0:5000

```

# A simple example

```python
from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swag = Swagger(app)

@swag.definition('user_response')
def get_user_response(username):
    """
    user response
    ---
    properties:
      username:
        type: string
        description: The username
        default: some_username
    """
    return {'username': username}
    

@app.route('/api/<string:username>')
def user_api(username):
    """
    User API
    This resource returns user information
    ---
    tags:
      - users
    parameters:
      - name: username
        in: path
        type: string
        required: true
    responses:
      200:
        description: A single user item
        schema:
          $ref: '#/definitions/user_response'
    """
    return jsonify(get_user_response(username))


app.run()

```

> NOTE: when catching arguments in path always use explicit types, bad: ``/api/<username>`` good: ``/api/<string:username>``

The api docs and playground for the above app will be available in [http://localhost:5000/apidocs/index.html](http://localhost:5000/apidocs/index.html)

## Inline Definitions

Route-specific definitions can also be defined inline by adding the 'id' 
attribute.  To avoid conflicts these definitions will be namespaced with the 
endpoint and verb.

```python
# This will add a definition named 'user_api_get_user_response'
@app.route('/api/<string:username>')
def user_api(username):
    """
    User API
    This resource returns user information
    ---
    tags:
      - users
    parameters:
      - name: username
        in: path
        type: string
        required: true
    responses:
      200:
        description: A single user item
        schema:
          id: user_response
          properties:
            username:
              type: string
              description: The username
              default: some_username
    """
    return jsonify({'username': username})
```

# using external files

If you don't like to put YAML on docstrings you can use an external file
using yaml or yml extension and following the same pattern.

### external_file.yml
```yaml
First line is the summary
All following lines until the hyphens is added to description
the format of the first lines until 3 hyphens will be not yaml compliant
but everything below the 3 hyphens should be.
---
tags:
  - users
parameters:
  - in: path
    name: username
    type: string
    required: true
responses:
  200:
    description: A single user item
    schema:
      id: rec_username
      properties:
        username:
          type: string
          description: The name of the user
          default: 'steve-harris'

```

And then use this file as spec to a view

```python
from flasgger.utils import swag_from

@app.route('/api/<string:username>')
@swag_from('path/to/external_file.yml')
def fromfile_decorated(username):
    return jsonify({'username': username})
```

Or if you don't  want to use the decorator you can simply use the shortcut

```python
@app.route('/api/<string:username>')
def fromfile_decorated(username):
    """
    file: path/to/external_file.yml
    """
    return jsonify({'username': username})

```

> NOTE: the above example only works for a single definition

# Handling multiple http methods and routes for a single function

You can separate specifications by endpoint or methods

```python
from flasgger.utils import swag_from

@app.route('/api/<string:username>', endpoint='with_user_name', methods=['PUT', 'GET'])
@app.route('/api/', endpoint='without_user_name')
@swag_from('path/to/external_file.yml', endpoint='with_user_name')
@swag_from('path/to/external_file_no_user_get.yml', endpoint='without_user_name', methods=['GET'])
@swag_from('path/to/external_file_no_user_put.yml', endpoint='without_user_name', methods=['PUT'])
def fromfile_decorated(username=None):
    if not username:
        return "No user!"
    return jsonify({'username': username})
```

# Use the same yaml file to validate your API data

```
from flasgger.utils import validate, ValidationError

@swag_from('defs.yml')
def post():
    data = request.json
    try:
        validate(data, 'schema_id', 'defs.yml', __file__)
    except ValidationError:
        return abort(500)
```

All validation options can be found at http://json-schema.org/latest/json-schema-validation.html

# HTML sanitizer

By default Flasgger will try to sanitize the content in YAML definitions
replacing every ```\n``` with ```<br>``` but you can change this behaviour
setting another kind of sanitizer.

```
from flasgger import Swagger, NO_SANITIZER

app =Flask()
Swagger(app, sanitizer=NO_SANITIZER)
```

You can write your own sanitizer

```
Swagger(app, sanitizer=lambda text: do_anything_with(text))
```

There is also a Markdown parser available, if you want to be able to render
Markdown in your specs description use **MK_SANITIZER**


# More

flasgger supports docstrings in methods of MethodView classes (ala [Flask-RESTful](https://github.com/flask-restful/flask-restful)) and regular Flask view functions.

Following YAML conventions, flasgger searches for `---`, everything preceding is provided as `summary` (first line) and `description` (following lines) for the endpoint while everything after is parsed as a swagger [Operation](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#operation-object) object.

In order to support inline definition of [Schema ](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#schemaObject) objects in [Parameter](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#parameterObject)  and [Response](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#responsesObject) objects, flasgger veers a little off from the standard. We require an `id` field for the inline Schema which is then used to correctly place the [Schema](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#schemaObject) object in the [Definitions](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#definitionsObject) object.

[Schema ](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#schemaObject) objects can also be defined within the properties of other [Schema ](https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#schemaObject) objects . An example is shown above with the address property of User.


# example app

To expose your Swagger specification to the world you provide a Flask route that does something along these lines

This is the DEMO app included in **flasgger/example_app.py**

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
    # headers are optional, and default to an empty array. If specified, they overwrites the headers with the same key in your flask app.
    # "headers": [
    #     ('Access-Control-Allow-Origin', '*'),
    #     ('Access-Control-Allow-Headers', "Authorization, Content-Type"),
    #     ('Access-Control-Expose-Headers', "Authorization"),
    #     ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
    #     ('Access-Control-Allow-Credentials', "true"),
    #     ('Access-Control-Max-Age', 60 * 60 * 24 * 20),
    # ],
    # other optional settings
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
            # ),
            
            # definition_filter is optional
            # it is a callable to filter the definition models to include
            
            # "definition_filter": lambda definition: (
            #     'v1_model' in definition.tags
            # )
        }
    ]
}

swag = Swagger(app)  # you can pass config here Swagger(app, config={})


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
                    $ref: '#/definitions/should_be_v1_only_users_post_User'
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
                    $ref: '#/definitions/should_be_v1_only_users_post_User'
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


if __name__ == "__main__":
    app.run(debug=True)

```

then access [http://localhost:5000/apidocs/index.html](http://localhost:5000/apidocs/index.html) to see api docs in action

Acknowledgments

Flasgger uses Swagger UI [Swagger-UI](https://github.com/swagger-api/swagger-ui)


Flasgger is a fork of [Flask-Swagger](https://github.com/gangverk/flask-swagger) which is a simpler solution, consider it if you just want to expose specs json.
