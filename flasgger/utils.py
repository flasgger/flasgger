# coding: utf-8

import os
import jsonschema
from jsonschema import ValidationError  # noqa
from functools import wraps
from .base import _extract_definitions, yaml, load_from_file


def swag_from(filepath, filetype=None):
    """
    filepath is complete path to open the file
    filetype is yml, json, py
       if None will be inferred
    """
    def decorator(function):
        # function.__code__.co_filename # option to access filename
        if not filepath.startswith('/'):
            final_filepath = os.path.join(
                os.path.dirname(function.func_globals['__file__']), filepath
            )
        else:
            final_filepath = filepath
        function.swag_path = final_filepath
        function.swag_type = filetype or filepath.split('.')[-1]
        if function.swag_type not in ('yaml', 'yml'):
            raise AttributeError("only yaml or yml supported")

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
    if not filepath.startswith('/'):
        final_filepath = os.path.join(os.path.dirname(root), filepath)
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
    raw_definitions = _extract_definitions(params)
    for defi in raw_definitions:
        if defi['id'] == schema_id:
            main_def = defi.copy()
        else:
            definitions[defi['id']] = defi
    main_def['definitions'] = definitions
    for key, value in definitions.items():
        del value['id']
    jsonschema.validate(data, main_def)
