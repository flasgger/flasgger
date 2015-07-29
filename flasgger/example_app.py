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
    "title": "Flasgger",
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
            "rule_filter": lambda rule: rule.endpoint.startswith(
                'should_be_v1_only'
            )
        },
        {
            "version": "0.0.2",
            "title": "Api v2",
            "endpoint": 'v2_spec',
            "route": '/v2/spec',
            "rule_filter": lambda rule: rule.endpoint.startswith(
                'should_be_v2_only'
            )
        }
    ]
}

swagger = Swagger(app)  # you can pass config here Swagger(config={})


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
    methods=["GET"],
    endpoint='should_be_v1_only_users'
)
app.add_url_rule(
    '/v1/testing/<int:team_id>',
    view_func=view,
    endpoint='should_be_v1_only_testing'
)


@app.route("/v2/resource", endpoint="should_be_v2_only")
def bla():
    """
    An endpoint that isn't using method view
    ---
    tags:
    - hacks
    responses:
      200:
        description: Hacked some hacks
        schema:
          id: Hack
          properties:
            hack:
              type: string
              description: it's a hack
            subitems:
              type: array
              items:
                schema:
                  id: SubItem
                  properties:
                    bla:
                      type: string
                      description: Bla
                    blu:
                      type: integer
                      description: Blu

    """

    data = {
        "hack": "string",
        "subitems": [
            {
                "bla": "string",
                "blu": 0
            }
        ]
    }
    return jsonify(data)


@app.route("/")
def hello():
    return """
      <h1> Welcome to Flasgger demo application</h1>
      This app exposes two API versions
      <ul>
         <li><a href="/apidocs/index.html?url=/v1/spec">Api Version 1</a></li>
         <li><a href="/apidocs/index.html?url=/v2/spec">Api Version 2</a></li>
      </ul>
    <p>
      As you can see the APIs is served by the same swagger UI on
      <a href="/apidocs/index.html">Api docs</a>
     </p>
     <p>
      Flasgger <a href="https://github.com/rochacbruno/flasgger">
      https://github.com/rochacbruno/flasgger</a>
    </p>
    """


if __name__ == "__main__":
    app.run(debug=True)
