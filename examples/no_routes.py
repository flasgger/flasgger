"""
In this example nothing is swagged
this is useful for testing if Swagger is ignoring
no swagabble views.
"""
from flask import Flask
from flask.views import MethodView

from flasgger import Swagger

app = Flask(__name__)
swag = Swagger()


@app.route('/')
def index():
    return 'Hello World'


class TestView(MethodView):
    def get(self):
        return 'Hello World'


class Meow(MethodView):
    """
    This is to ensure Swagger does not break with empty MethodViews
    issue #76
    """
    pass

app.add_url_rule(
    '/meow/<int:param>/',
    view_func=Meow.as_view('meow'),
    methods=['DELETE']
)


app.add_url_rule(
    '/testview',
    view_func=TestView.as_view('testview'),
    methods=['GET']
)


if __name__ == '__main__':
    swag.init_app(app)
    app.run(debug=True)
