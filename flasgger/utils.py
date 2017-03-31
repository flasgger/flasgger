# coding: utf-8

import copy
import inspect
import os
from collections import OrderedDict
from copy import deepcopy
from functools import wraps

import jsonschema
import yaml
from flask import Response, abort, request
from jsonschema import ValidationError  # noqa
from six import string_types

from flasgger.base import _extract_definitions, load_from_file


def swag_from(specs=None, filetype=None, endpoint=None, methods=None,
              validation=False, schema_id=None, data=None, definition=None):
    """
    Takes a filename.yml, a dictionary or object and loads swagger specs.

    :param specs: a filepath, a dictionary or an object
    :param filetype: yml or yaml (json and py to be implemented)
    :param endpoint: endpoint to build definition name
    :param methods: method to build method based specs
    :param validation: perform validation?
    :param schema_id: Definition id ot name to use for validation
    :param data: data to validate (default is request.json)
    :param definition: alias to schema_id
    """

    def resolve_path(function, filepath):
        if not filepath.startswith('/'):
            if not hasattr(function, 'root_path'):
                function.root_path = os.path.dirname(
                    os.path.abspath(
                        function.__globals__['__file__']
                    )
                )
            res = os.path.join(function.root_path, filepath)
            return res
        return filepath

    def set_from_filepath(function):
        final_filepath = resolve_path(function, specs)
        function.swag_type = filetype or specs.split('.')[-1]

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

    def set_from_specs_dict(function):
        function.specs_dict = specs

    def decorator(function):

        if isinstance(specs, string_types):
            set_from_filepath(function)
            # function must have or a single swag_path or a list of them
            swag_path = getattr(function, 'swag_path', None)
            swag_paths = getattr(function, 'swag_paths', None)
            validate_args = {
                'filepath': swag_path or swag_paths,
                'root': getattr(function, 'root_path', None)
            }
        if isinstance(specs, dict):
            set_from_specs_dict(function)
            validate_args = {'specs': specs}

        @wraps(function)
        def wrapper(*args, **kwargs):
            if validation is True:
                validate(
                    data,
                    schema_id or definition,
                    **validate_args
                )
            return function(*args, **kwargs)
        return wrapper

    return decorator


def validate(data=None, schema_id=None, filepath=None, root=None,
             definition=None, specs=None):
    """
    This method is available to use YAML swagger definitions file
    or specs (dict or object) to validate data against its jsonschema.

    example:
        validate({"item": 1}, 'item_schema', 'defs.yml', root=__file__)
        validate(request.json, 'User', specs={'definitions': {'User': ...}})

    :param data: data to validate, by defaull is request.json
    :param schema_id: The definition id to use to validate (from specs)
    :param filepath: definition filepath to load specs
    :parm root: root folder (inferred if not provided), unused if path starts
        with `/`
    :param definition: Alias to schema_id (kept for backwards compatibility)
    :param specs: load definitions from dict or object passed here intead of
        a file.
    """
    schema_id = schema_id or definition

    # for backwards compatibility with function signature
    if filepath is None and specs is None:
        abort(Response('Filepath or specs is needed to validate', status=500))

    if data is None:
        data = request.json  # defaults
    elif callable(data):
        # data=lambda: request.json
        data = data()

    if not data:
        abort(Response('No data to validate', status=500))

    # not used anymore but kept to reuse with marshmallow
    endpoint = request.endpoint.lower().replace('.', '_')
    verb = request.method.lower()

    if filepath is not None:
        if not root:
            try:
                frame_info = inspect.stack()[1]
                root = os.path.dirname(os.path.abspath(frame_info[1]))
            except Exception:
                root = None
        else:
            root = os.path.dirname(root)

        if not filepath.startswith('/'):
            final_filepath = os.path.join(root, filepath)
        else:
            final_filepath = filepath
        full_doc = load_from_file(final_filepath)
        yaml_start = full_doc.find('---')
        swag = yaml.load(full_doc[yaml_start if yaml_start >= 0 else 0:])
    else:
        swag = copy.deepcopy(specs)

    params = [
        item for item in swag.get('parameters', [])
        if item.get('schema')
    ]

    definitions = {}
    main_def = {}
    raw_definitions = _extract_definitions(
        params, endpoint=endpoint, verb=verb)

    if schema_id is None:
        for param in params:
            if param.get('in') == 'body':
                schema_id = param.get('schema', {}).get('$ref')
                if schema_id:
                    schema_id = schema_id.split('/')[-1]
                    break  # consider only the first

    if schema_id is None:
        # if it is still none use first raw_definition extracted
        if raw_definitions:
            schema_id = raw_definitions[0].get('id')

    for defi in raw_definitions:
        if defi['id'].lower() == schema_id.lower():
            main_def = defi.copy()
        else:
            definitions[defi['id']] = defi

    # support definitions informed in dict
    if schema_id in swag.get('definitions', {}):
        main_def = swag.get('definitions', {}).get(schema_id)

    main_def['definitions'] = definitions

    for key, value in definitions.items():
        if 'id' in value:
            del value['id']

    try:
        jsonschema.validate(data, main_def)
    except ValidationError as e:
        abort(Response(str(e), status=400))


def apispec_to_template(app, spec, definitions=None, paths=None):
    """
    Converts apispec object in to flasgger definitions template
    :param app: Current app
    :param spec: apispec.APISpec
    :param definitions: a list of [Schema, ..] or [('Name', Schema), ..]
    :param paths: A list of flask views
    """
    definitions = definitions or []
    paths = paths or []
    spec_dict = spec.to_dict()

    with app.app_context():
        for definition in definitions:
            if isinstance(definition, (tuple, list)):
                name, schema = definition
            else:
                schema = definition
                name = schema.__name__.replace('Schema', '')

            spec.definition(name, schema=schema)

        for path in paths:
            spec.add_path(view=path)

    ret = ordered_dict_to_dict(spec_dict)
    return ret


def ordered_dict_to_dict(d):
    """
    Converts inner OrderedDict to bare dict
    """
    ret = {}
    new_d = deepcopy(d)
    for k, v in new_d.items():
        if isinstance(v, OrderedDict):
            v = dict(v)
        if isinstance(v, dict):
            v = ordered_dict_to_dict(v)
        ret[k] = v
    return ret
