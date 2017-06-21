"""
A test to ensure that MethodView inheritance works as expected
"""
from flask import Flask, jsonify
from flask.views import MethodView

from flasgger import Swagger


class BaseAPIView(MethodView):
    """BAse view"""


class ModelAPIView(BaseAPIView):
    """Model api view"""


class PostAPIView(ModelAPIView):

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
            type: int32
        definitions:
          User:
            type: object
            properties:
              name:
                type: string
              team:
                type: int32
        responses:
          200:
            description: Returns a list of users
            schema:
              id: Users
              type: object
              properties:
                users:
                  type: array
                  items:
                    $ref: '#/definitions/User'
            examples:
              users: [{'name': 'Russel Allen', 'team': 66}]
        """
        data = {
            "users": [
                {"name": "Steven Wilson", "team": team_id},
                {"name": "Mikael Akerfeldt", "team": team_id},
                {"name": "Daniel Gildenlow", "team": team_id}
            ]
        }
        return jsonify(data)


app = Flask(__name__)
swag = Swagger(app)

app.add_url_rule(
    '/user/<team_id>',
    view_func=PostAPIView.as_view('user'),
    methods=['GET']
)

if __name__ == "__main__":
    app.run(debug=True)
