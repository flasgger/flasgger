#!/usr/bin/python3
import pytest
import sys
import flask_openapi
import flask
import json
from collections import defaultdict

def test_client():
    class FakeJson():
        def dumps(self, *args, **kwargs):
            """
            Raises a type error
            """
            raise TypeError
    flask.json._json = FakeJson()
    app = flask.Flask('test-app')
    flask_openapi.base.jsonify = flask.jsonify
    with app.app_context():
        specs = flask_openapi.base.APISpecsView(loader=lambda: {'test': 'test'})
        assert specs.get() != None
    flask.json._json = json
