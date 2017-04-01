"""
A general example
"""
from flask import Flask, jsonify, request
from flask.views import MethodView

from flasgger import Swagger
from flasgger.utils import swag_from

app = Flask(__name__)


# config your API specs
# you can define multiple specs in the case your api has multiple versions
# ommit configs to get the default (all views exposed in /spec url)
# rule_filter is a callable that receives "Rule" object and
#   returns a boolean to filter in only desired views

app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "title": "Flasgger",
    "headers": [
        ('Access-Control-Allow-Origin', '*'),
        ('Access-Control-Allow-Methods', "GET, POST, PUT, DELETE, OPTIONS"),
        ('Access-Control-Allow-Credentials', "true"),
    ],
    "specs": [
        {
            "version": "0.0.1",
            "title": "Api v1",
            "endpoint": 'v1_spec',
            "description": 'This is the version 1 of our API',
            "route": '/v1/spec',
            # rule_filter is optional
            # it is a callable to filter the views to extract
            "rule_filter": lambda rule: rule.endpoint.startswith(
                'should_be_v1_only'
            ),
            # definition_filter is optional
            # it is a callable to filter the definition models to include
            "definition_filter": lambda definition: (
                'v1_model' in definition.tags)
        },
        {
            "version": "0.0.2",
            "title": "Api v2",
            "description": 'This is the version 2 of our API',
            "endpoint": 'v2_spec',
            "route": '/v2/spec',
            "rule_filter": lambda rule: rule.endpoint.startswith(
                'should_be_v2_only'
            ),
            "definition_filter": lambda definition: (
                'v2_model' in definition.tags)
        }
    ]
}

swag = Swagger(app)  # you can pass config here Swagger(config={})


@app.after_request
def allow_origin(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://example.com'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response


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
            default: 42
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

    def post(self):
        """
        Create a new user
        First line is the summary
        All following lines until the hyphens is added to description
        ---
        tags:
          - users
        parameters:
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
                  default: 42
                name:
                  type: string
                  description: name for user
                  default: Russel Allen
        responses:
          201:
            description: New user created
            schema:
                type: array
                items:
                    $ref: '#/definitions/User'
          import: "not_found.yaml"
        """
        return jsonify(
            {"data": request.json, "status": "New user created"}
        ), 201


view = UserAPI.as_view('users')
app.add_url_rule(
    '/v1/users/<int:team_id>',
    view_func=view,
    methods=['GET'],
    endpoint='should_be_v1_only'
)
app.add_url_rule(
    '/v1/users',
    view_func=view,
    methods=['POST'],
    endpoint='should_be_v1_only_post'
)

# LOADING SPECS FROM EXTERNAL FILE


@app.route('/v1/decorated/<username>', endpoint='should_be_v1_only_username')
@swag_from('username_specs.yml')
def fromfile_decorated(username):
    return jsonify({'username': username})


# OR


@app.route('/v1/fileindoc/<username>', endpoint='should_be_v1_only_username_1')
def fromfile_indocstring(username):
    """
    file: username_specs.yml
    """
    return jsonify({'username': username})


# DEFINITIONS FROM OBJECTS

@swag.definition('Hack', tags=['v2_model'])
def hack(subitems):
    """
    Hack Object
    ---
    properties:
      hack:
        type: string
        description: it's a hack
      subitems:
        type: array
        items:
          $ref: '#/definitions/SubItem'
    """
    return {
        'hack': "string",
        'subitems': [subitem.dump() for subitem in subitems]
    }


@swag.definition('SubItem', tags=['v2_model'])
class SubItem(object):
    """
    SubItem Object
    ---
    properties:
      bla:
        type: string
        description: Bla
      blu:
        type: integer
        description: Blu
    """
    def __init__(self, bla, blu):
        self.bla = str(bla)
        self.blu = int(blu)

    def dump(self):
        return dict(vars(self).items())


@app.route("/v2/resource", endpoint="should_be_v2_only")
def bla():
    """
    An endpoint that isn't using method view
    ---
    tags:
    - hacking
    responses:
      200:
        description: Hacked some hacks
        schema:
          $ref: '#/definitions/Hack'
    """
    subitems = [SubItem("string", 0)]
    return jsonify(hack(subitems))


@swag.definition('rec_query_context', tags=['v2_model'])
class RecQueryContext(object):
    """
    Recommendation Query Context
    ---
    required:
      - origin
    properties:
      origin:
        type: string
        default: sugestao
      last_event:
        type: object
        schema:
          $ref: '#/definitions/rec_query_context_last_event'
    """
    def __init__(self, origin, last_event=None):
        self.origin = origin
        self.last_event = last_event

    def dump(self):
        data = {'origin': self.origin}
        if self.last_event:
            data.update({'last_event': self.last_event.dump()})
        return data


@swag.definition('rec_query_context_last_event', tags=['v2_model'])
class RecQueryContextLastEvent(object):
    """
    RecQueryContext Last Event Definition
    ---
    properties:
      event:
        type: string
        default: apply
      data:
        type: object
        schema:
          $ref: '#/definitions/rec_query_context_last_event_data'
    """
    def __init__(self, event=None, data=None):
        self.event = event
        self.data = data

    def dump(self):
        data = {}
        if self.event:
            data.update({'event': self.event})
        if self.data:
            data.update({'data': self.data.dump()})
        return data


@swag.definition('rec_query_context_last_event_data', tags=['v2_model'])
class RecQueryContextLastEventData(object):
    """
    RecQueryContextLastEvent Data Object
    ---
    properties:
      candidate_id:
        type: integer
        default: 123456
      opening_id:
        type: integer
        default: 324345435
      company_id:
        type: integer
        default: 324345435
      datetime:
        type: string
        format: date-time
        default: 2014-09-10T11:41:00.12343-03:00
      recruiter_id:
        type: integer
        default: 435345
      context:
        $ref: '#/definitions/rec_query_context'
    """
    def __init__(self, candidate_id=None, opening_id=None, company_id=None,
                 datetime=None, recruiter_id=None):
        self.candidate_id = candidate_id
        self.opening_id = opening_id
        self.company_id = company_id
        self.datetime = datetime
        self.recruiter_id = recruiter_id

    def dump(self):
        data = {}
        for var in ['candidate_id', 'opening_id', 'company_id', 'datetime',
                    'recruiter_id']:
            if var in vars(self):
                data.update({var: vars(self)[var]})
        return data


@app.route("/v2/recommendation/<target_type>/<item_type>", methods=['POST'],
           endpoint="should_be_v2_only_recommendation")
def recommend(target_type, item_type):
    """
    Recommendation
    Get a single item_type as recommendation for the target_type
    ---
    tags:
      - recommendation
    parameters:
      - name: target_type
        in: path
        description: currently only "candidate" is supported
        required: true
        type: string
        default: candidate
      - name: item_type
        in: path
        description: currently only "openings" is supported
        required: true
        type: string
        default: openings
      - in: body
        name: body
        schema:
          id: rec_query
          required:
            - candidate_id
            - context
          properties:
            candidate_id:
              type: integer
              description: Id of the target (candidate / user)
              default: 123456
            exclude:
              type: array
              description: item_ids to exclude from recs
              default: [12345, 123456]
              items:
                  type: integer
            context:
              type: object
              schema:
                $ref: '#/definitions/rec_query_context'
    responses:
      200:
        description: A single recommendation item
        schema:
          id: rec_response
          properties:
            opening_id:
              type: integer
              description: The id of the opening
              default: 123456
      204:
         description: No recommendation found
    """

    data = {
        "opening_id": 12312313434
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
