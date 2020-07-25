#!/usr/bin/python3
import pytest
import sys
import flasgger
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
    flasgger.base.jsonify = flask.jsonify
    with app.app_context():
        specs = flasgger.base.APISpecsView(loader=lambda: {'test': 'test'})
        assert specs.get() != None
    flask.json._json = json
