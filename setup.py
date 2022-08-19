# Fix for older setuptools
import re
import os

from setuptools import setup, find_packages


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


def desc():
    return read('README.md')


# grep flask_openapi/__init__.py since python 3.x cannot
# import it before using 2to3
file_text = read(fpath('flask_openapi/__init__.py'))


def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, file_text)
    return strval


setup(
    name='Flask-OpenAPI',
    version=grep('__version__'),
    url='https://github.com/overflowdigital/Flask-OpenAPI/',
    license='MIT',
    author=grep('__author__'),
    author_email=grep('__email__'),
    description='Next generation OpenAPI v3 Integration for Flask based APIs. Based on Flasgger.',
    long_description=desc(),
    long_description_content_type="text/markdown",
    packages=find_packages(
        exclude=[
            'tests', 'tests.*',
            'examples', 'examples.*',
            'demo_app', 'demo_app.*',
            'etc', 'etc.*'
        ]
    ),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'PyYAML',
        'jsonschema',
        'mistune',
        'six'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'flask.commands': [
            'generate-api-schema=flasgger.commands:generate_api_schema',
        ],
    },
)
