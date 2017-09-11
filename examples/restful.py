"""
Example of Flask RESTFul integration.
requires: `pip install flask-restful`
"""
from flask import Flask
from flask_restful import Api, Resource, abort, reqparse

from flasgger import Swagger, swag_from

app = Flask(__name__)
api = Api(app)
app.config['SWAGGER'] = {
    'title': 'Flasgger RESTful',
    'uiversion': 2
}
swag = Swagger(app)


TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
    '42': {'task': 'Use Flasgger'}
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task')


# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        """
        This is an example
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: todo_id
            required: true
            description: The ID of the task, try 42!
            type: string
        responses:
          200:
            description: The task data
            schema:
              id: Task
              properties:
                task:
                  type: string
                  default: My Task
        """
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        """
        This is an example
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: todo_id
            required: true
            description: The ID of the task, try 42!
            type: string
        responses:
          204:
            description: Task deleted
        """
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        """
        This is an example
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Task'
          - in: path
            name: todo_id
            required: true
            description: The ID of the task, try 42!
            type: string
        responses:
          201:
            description: The task has been updated
            schema:
              $ref: '#/definitions/Task'
        """
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        """
        This is an example
        ---
        tags:
          - restful
        responses:
          200:
            description: The task data
            schema:
              id: Tasks
              properties:
                task_id:
                  type: object
                  schema:
                    $ref: '#/definitions/Task'
        """
        return TODOS

    def post(self):
        """
        This is an example
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Task'
        responses:
          201:
            description: The task has been created
            schema:
              $ref: '#/definitions/Task'
        """
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


class Username(Resource):
    @swag_from('username_specs.yml', methods=['GET'])
    def get(self, username):
        return {'username': username}, 200


api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')
api.add_resource(Username, '/username/<username>')


if __name__ == '__main__':
    app.run(debug=True)
