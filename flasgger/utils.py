# coding: utf-8

import os
from functools import wraps


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
