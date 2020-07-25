#!/usr/bin/python3
import pytest
import os
import sys
sys.path.insert(0, '..')
import flasgger
import json
import flask
import tempfile
from flask_testing import TestCase
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
