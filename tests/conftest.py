import os
from importlib import import_module

import pytest


EXAMPLES_DIR = "examples/"


def remove_suffix(fpath):
    """Remove all file ending suffixes"""
    return os.path.splitext(fpath)[0]


def is_python_file(fpath):
    """Naive Python module filterer"""
    return ".py" in fpath and "__" not in fpath


def pathify(basenames):
    """*nix to python module path"""
    example = EXAMPLES_DIR.replace("/", ".")
    return [example + basename for basename in basenames]


@pytest.fixture
def examples():
    """All example modules"""
    all_files = os.listdir(EXAMPLES_DIR)
    python_files = [f for f in all_files if is_python_file(f)]
    basenames = [remove_suffix(f) for f in python_files]
    return [import_module(module) for module in pathify(basenames)]
