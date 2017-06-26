# Flasgger
## Easy Swagger UI for your Flask API

[![Build Status](https://travis-ci.org/rochacbruno/flasgger.svg?branch=master)](https://travis-ci.org/rochacbruno/flasgger)
[![Code Health](https://landscape.io/github/rochacbruno/flasgger/master/landscape.svg?style=flat)](https://landscape.io/github/rochacbruno/flasgger/master)
[![Coverage Status](https://coveralls.io/repos/github/rochacbruno/flasgger/badge.svg?branch=master)](https://coveralls.io/github/rochacbruno/flasgger?branch=master)
[![PyPI](https://img.shields.io/pypi/v/flasgger.svg)](https://pypi.python.org/pypi/flasgger)
 <a target="_blank" href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&amp;business=rochacbruno%40gmail%2ecom&amp;lc=BR&amp;item_name=Flasgger&amp;no_note=0&amp;currency_code=USD&amp;bn=PP%2dDonationsBF%3abtn_donate_SM%2egif%3aNonHostedGuest"><img alt='Donate with Paypal' src='http://www.paypalobjects.com/en_US/i/btn/btn_donate_SM.gif' /></a>


![flasgger](docs/flasgger.png)

Flasgger is a Flask extension to **extract [OpenAPI=Specification](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#operation-object)** from all Flask views registered in your API.

Flasgger also comes with **[SwaggerUI](http://swagger.io/swagger-ui/) embedded** so you can access [http://localhost:5000/apidocs](localhost:5000/apidocs) and visualize and interact with your API resources.

Flasgger also **provides validation** of the incoming data, using the same specification it can validates if the data received as as a POST, PUT, PATCH is valid against the schema defined using **YAML**, **Python dictionaries** or **Marshmallow Schemas**.

Flasgger can work with simple function views or MethodViews using docstring for especification, or using `@swag_from` decorator to get specification from **YAML** or **dict** and also provides **SwaggerView** which can use **Marshmallow Schemas**  as specification.

Flasgger is compatible with `Flask-RESTful` so you can use `Resources` and `swag` specifications together, take a look at [restful example.](examples/restful.py)

Flasgger also supports `Marshmallow APISpec` as base template for specification, if you are using APISPec from Marshmallow take a look at [apispec example.](examples/apispec_example.py)

# Examples and demo app

There are some [example applications](examples/) and you can also play with examples in [Flasgger demo app](http://flasgger.pythonanywhere.com/)

> NOTE: all the examples apps are also test cases and run automatically in Travis CI to ensure quality and coverage.

# Installation

> under your virtualenv do:

```
pip install flasgger
```

or (dev version)

```
pip install https://github.com/rochacbruno/flasgger/tarball/master
```

> NOTE: If you want to use **Marshmallow Schemas** you also need to run `pip install marshmallow apispec`

# Getting started

## Using docstrings as specification

Create a file called for example `colors.py`

```python
from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/colors/<palette>/')
def colors(palette):
    """Example endpoint returning a list of colors by palette
    This is using docstrings for specifications.
    ---
    parameters:
      - name: palette
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
        required: true
        default: all
    definitions:
      Palette:
        type: object
        properties:
          palette_name:
            type: array
            items:
              $ref: '#/definitions/Color'
      Color:
        type: string
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          $ref: '#/definitions/Palette'
        examples:
          rgb: ['red', 'green', 'blue']
    """
    all_colors = {
        'cmyk': ['cian', 'magenta', 'yellow', 'black'],
        'rgb': ['red', 'green', 'blue']
    }
    if palette == 'all':
        result = all_colors
    else:
        result = {palette: all_colors.get(palette)}

    return jsonify(result)

app.run(debug=True)
```

Now run:

```
python colors.py
```

And go to: [http://localhost:5000/apidocs/](http://localhost:5000/apidocs/)

You should get:

![colors](docs/colors.png)

## Using external YAML files

Save a new file `colors.yml`

```yaml
Example endpoint returning a list of colors by palette
In this example the specification is taken from external YAML file
---
parameters:
  - name: palette
    in: path
    type: string
    enum: ['all', 'rgb', 'cmyk']
    required: true
    default: all
definitions:
  Palette:
    type: object
    properties:
      palette_name:
        type: array
        items:
          $ref: '#/definitions/Color'
  Color:
    type: string
responses:
  200:
    description: A list of colors (may be filtered by palette)
    schema:
      $ref: '#/definitions/Palette'
    examples:
      rgb: ['red', 'green', 'blue']
```


lets use the same example changing only the view function.

```python
from flasgger import swag_from

@app.route('/colors/<palette>/')
@swag_from('colors.yml')
def colors(palette):
    ...
```

If you do not want to use the decorator you can use the docsting `file:` shortcut.

```python
@app.route('/colors/<palette>/')
def colors(palette):
    """
    file: colors.yml
    """
    ...
```


## Using dictionaries as raw specs

Create a Python dictionary as:

```python
specs_dict = {
  "parameters": [
    {
      "name": "palette",
      "in": "path",
      "type": "string",
      "enum": [
        "all",
        "rgb",
        "cmyk"
      ],
      "required": true,
      "default": "all"
    }
  ],
  "definitions": {
    "Palette": {
      "type": "object",
      "properties": {
        "palette_name": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/Color"
          }
        }
      }
    },
    "Color": {
      "type": "string"
    }
  },
  "responses": {
    "200": {
      "description": "A list of colors (may be filtered by palette)",
      "schema": {
        "$ref": "#/definitions/Palette"
      },
      "examples": {
        "rgb": [
          "red",
          "green",
          "blue"
        ]
      }
    }
  }
}
```

Now take the same function and use the dict in the place of YAML file.

```python
@app.route('/colors/<palette>/')
@swag_from(specs_dict)
def colors(palette):
    """Example endpoint returning a list of colors by palette
    In this example the specification is taken from specs_dict
    """
    ...
```

## Using Marshmallow Schemas

> FIRST: `pip install marshmallow apispec`

```python
from flask import Flask, jsonify
from flasgger import Swagger, SwaggerView, Schema, fields


class Color(Schema):
    name = fields.Str()

class Palette(Schema):
    pallete_name = fields.Str()
    colors = fields.Nested(Color, many=True)

class PaletteView(SwaggerView):
    parameters = [
        {
            "name": "palette",
            "in": "path",
            "type": "string",
            "enum": ["all", "rgb", "cmyk"],
            "required": True,
            "default": "all"
        }
    ]
    responses = {
        200: {
            "description": "A list of colors (may be filtered by palette)",
            "schema": Palette
        }
    }

    def get(self, palette):
        """
        Colors API using schema
        This example is using marshmallow schemas
        """
        all_colors = {
            'cmyk': ['cian', 'magenta', 'yellow', 'black'],
            'rgb': ['red', 'green', 'blue']
        }
        if palette == 'all':
            result = all_colors
        else:
            result = {palette: all_colors.get(palette)}
        return jsonify(result)

app = Flask(__name__)
swagger = Swagger(app)

app.add_url_rule(
    '/colors/<palette>',
    view_func=PaletteView.as_view('colors'),
    methods=['GET']
)

app.run(debug=True)

```

> NOTE: take a look at `examples/validation.py` for a more complete example.


> NOTE: when catching arguments in path rule always use explicit types, bad: ``/api/<username>`` good: ``/api/<string:username>``


## Using **Flask RESTful** Resources

Flasgger is compatible with Flask-RESTful you only need to install `pip install flask-restful` and then:

```python

from flask import Flask
from flasgger import Swagger
from flask_restful import Api, Resource

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

class Username(Resource):
    def get(self, username):
       """
       This examples uses FlaskRESTful Resource
       It works also with swag_from, schemas and spec_dict
       ---
       parameters:
         - in: path
           name: username
           type: string
           required: true
       responses:
         200:
           description: A single user item
           schema:
             id: User
             properties:
               username:
                 type: string
                 description: The name of the user
                 default: Steven Wilson
        """
        return {'username': username}, 200


api.add_resource(Username, '/username/<username>')

app.run(debug=True)

```

## Handling multiple http methods and routes for a single function

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

And the same can be achieved with multiple methods in a `MethodView` or `SwaggerView` by
registering the `url_rule` many times. Take a look at `examples/example_app`


# Use the same data to validate your API POST body.

Setting `swag_from`'s _validation_ parameter to `True` will validate incoming data automatically:

```python
from flasgger import swag_from

@swag_from('defs.yml', validation=True)
def post():
    # if not validate returns ValidationError response with status 400
    # also returns the validation message.
```

Using `swagger.validate` annotation is also possible:

```python
from flasgger import Swagger

swagger = Swagger(app)

@swagger.validate('UserSchema')
def post():
    '''
    file: defs.yml
    '''
    # if not validate returns ValidationError response with status 400
    # also returns the validation message.
```

Yet you can call `validate` manually:

```python
from flasgger import swag_from, validate

@swag_from('defs.yml')
def post():
    validate(request.json, 'UserSchema', 'defs.yml')
    # if not validate returns ValidationError response with status 400
    # also returns the validation message.
```

It is also possible to define `validation=True` in `SwaggerView` and also use
`specs_dict` for validation.

Take a look at `examples/validation.py` for more information.

All validation options can be found at http://json-schema.org/latest/json-schema-validation.html

# HTML sanitizer

By default Flasgger will try to sanitize the content in YAML definitions
replacing every ```\n``` with ```<br>``` but you can change this behaviour
setting another kind of sanitizer.

```python
from flasgger import Swagger, NO_SANITIZER

app =Flask()
swagger = Swagger(app, sanitizer=NO_SANITIZER)
```

You can write your own sanitizer

```python
swagger = Swagger(app, sanitizer=lambda text: do_anything_with(text))
```

There is also a Markdown parser available, if you want to be able to render
Markdown in your specs description use **MK_SANITIZER**


# Swagger UI and templates

You can override the `templates/flasgger/index.html` in your application and
this template will be the `index.html` for SwaggerUI. Use `flasgger/ui2/templates/index.html`
as base for your customization.

Flasgger supports Swagger UI versions 2 and 3, The version 3 is still experimental but you
can try setting `app.config['SWAGGER']['uiversion']`.

```python
app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'My API',
    'uiversion': 3
}
swagger = Swagger(app)

```

# Initializing Flasgger with default data.

You can start your Swagger spec with any default data providing a template:

```python
template = {
  "swagger": "2.0",
  "info": {
    "title": "My API",
    "description": "API for my data",
    "contact": {
      "responsibleOrganization": "ME",
      "responsibleDeveloper": "Me",
      "email": "me@me.com",
      "url": "www.me.com",
    },
    "termsOfService": "http://me.com/terms",
    "version": "0.0.1"
  },
  "host": "mysite.com",  # overrides localhost:500
  "basePath": "/api",  # base bash for blueprint registration
  "schemes": [
    "http",
    "https"
  ],
  "operationId": "getmyData"
}

swagger = Swagger(app, template=template)

```

And then the template is the default data unless some view changes it. You
can also provide all your specs as template and have no views. Or views in
external APP.

# Customize default configurations

Custom configurations such as a different specs route or disabling Swagger UI can be provided to Flasgger:

```python
swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger = Swagger(app, config=swagger_config)

```

## Extracting Definitions

Definitions can be extracted when `id` is found in spec, example:

```python
from flask import Flask, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

@app.route('/colors/<palette>/')
def colors(palette):
    """Example endpoint returning a list of colors by palette
    ---
    parameters:
      - name: palette
        in: path
        type: string
        enum: ['all', 'rgb', 'cmyk']
        required: true
        default: all
    responses:
      200:
        description: A list of colors (may be filtered by palette)
        schema:
          id: Palette
          type: object
          properties:
            palette_name:
              type: array
              items:
                schema:
                  id: Color
                  type: string
        examples:
          rgb: ['red', 'green', 'blue']
    """
    all_colors = {
        'cmyk': ['cian', 'magenta', 'yellow', 'black'],
        'rgb': ['red', 'green', 'blue']
    }
    if palette == 'all':
        result = all_colors
    else:
        result = {palette: all_colors.get(palette)}

    return jsonify(result)

app.run(debug=True)
```

In this example you do not have to pass `definitions` but need to add `id` to
your schemas.

