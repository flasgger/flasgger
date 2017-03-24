# coding: utf-8

import os
import inspect
from functools import wraps

import jsonschema
import yaml
from flask import request, abort, Response
from jsonschema import ValidationError  # noqa

from .base import _extract_definitions, load_from_file


def swag_from(filepath, filetype=None, endpoint=None, methods=None):
    """
    filepath is complete path to open the file
    filetype is yml, json, py
       if None will be inferred
    If endpoint or methods is defined the definition will be
    exclusive
    """

    def resolve_path(function, filepath):
        if not filepath.startswith('/'):
            if not hasattr(function, 'root_path'):
                function.root_path = os.path.dirname(os.path.abspath(
                        function.__globals__['__file__']
                    )
                )
            res = os.path.join(function.root_path, filepath)
            return res
        return filepath

    def decorator(function):
        # function.__code__.co_filename # option to access filename

        final_filepath = resolve_path(function, filepath)
        function.swag_type = filetype or filepath.split('.')[-1]

        if endpoint or methods:
            if not hasattr(function, 'swag_paths'):
                function.swag_paths = {}

        if not endpoint and not methods:
            function.swag_path = final_filepath
        elif endpoint and methods:
            for verb in methods:
                key = "{}_{}".format(endpoint, verb.lower())
                function.swag_paths[key] = final_filepath
        elif endpoint and not methods:
            function.swag_paths[endpoint] = final_filepath
        elif methods and not endpoint:
            for verb in methods:
                function.swag_paths[verb.lower()] = final_filepath

        @wraps(function)
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)
        return wrapper
    return decorator


def validate(data, schema_id, filepath, root=None):
    """
    This method is available to use YAML swagger definitions file
    to validate data against its jsonschema.
    example:
    validate({"item": 1}, 'item_schema', 'defs.yml', root=__file__)
    If root is not defined it will try to use absolute import so path
    should start with /
    """

    if not root:
        try:
            frame_info = inspect.stack()[1]
            root = os.path.dirname(os.path.abspath(frame_info[1]))
            print(root)
        except Exception:
            root = None
    else:
        root = os.path.dirname(root)

    endpoint = request.endpoint.lower().replace('.', '_')
    verb = request.method.lower()

    full_schema = "{}_{}_{}".format(endpoint, verb, schema_id)

    if not filepath.startswith('/'):
        final_filepath = os.path.join(root, filepath)
    else:
        final_filepath = filepath
    full_doc = load_from_file(final_filepath)
    yaml_start = full_doc.find('---')
    swag = yaml.load(full_doc[yaml_start if yaml_start >= 0 else 0:])
    params = [
        item for item in swag.get('parameters', [])
        if item.get('schema')
    ]

    definitions = {}
    main_def = {}
    raw_definitions = _extract_definitions(
        params, endpoint=endpoint, verb=verb)

    for defi in raw_definitions:
        if defi['id'] in [schema_id, full_schema]:
            main_def = defi.copy()
        else:
            definitions[defi['id']] = defi

    main_def['definitions'] = definitions

    for key, value in definitions.items():
        del value['id']

    try:
        jsonschema.validate(data, main_def)
    except ValidationError as e:
        abort(Response(str(e), status=400))
