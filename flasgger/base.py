"""
What's the big idea?

An endpoint that traverses all restful endpoints producing a swagger 2.0 schema
If a swagger yaml description is found in the docstrings for an endpoint
we add the endpoint to swagger specification output

"""
import inspect
import os
import re
from collections import defaultdict

import yaml
from flask import (Blueprint, Markup, current_app, jsonify, redirect,
                   render_template, request, url_for)
from flask.views import MethodView
from mistune import markdown

NO_SANITIZER = lambda text: text  # noqa
BR_SANITIZER = lambda text: text.replace('\n', '<br/>') if text else text  # noqa
MK_SANITIZER = lambda text: Markup(markdown(text)) if text else text  # noqa


def get_path_from_doc(full_doc):
    swag_path = full_doc.replace('file:', '').strip()
    swag_type = swag_path.split('.')[-1]
    return swag_path, swag_type


def json_to_yaml(content):
    """
    TODO: convert json to yaml
    """
    return content


def load_from_file(swag_path, swag_type='yml'):
    if swag_type not in ('yaml', 'yml'):
        raise AttributeError("Currently only yaml or yml supported")
        # TODO: support JSON
    try:
        with open(swag_path) as yaml_file:
            return yaml_file.read()
    except IOError:
        # not in the same dir, add dirname
        swag_path = os.path.join(os.path.dirname(__file__), swag_path)
        with open(swag_path) as yaml_file:
            return yaml_file.read()


def _parse_docstring(obj, process_doc, endpoint=None, verb=None):
    first_line, other_lines, swag = None, None, None

    full_doc = None
    swag_path = getattr(obj, 'swag_path', None)
    swag_type = getattr(obj, 'swag_type', 'yml')
    swag_paths = getattr(obj, 'swag_paths', None)

    if swag_path is not None:
        full_doc = load_from_file(swag_path, swag_type)
    elif swag_paths is not None:
        for key in ("{}_{}".format(endpoint, verb), endpoint, verb.lower()):
            if key in swag_paths:
                full_doc = load_from_file(swag_paths[key], swag_type)
                break
    else:
        full_doc = inspect.getdoc(obj)

    if full_doc:

        if full_doc.startswith('file:'):
            if not hasattr(obj, 'root_path'):
                obj.root_path = os.path.dirname(os.path.abspath(
                        obj.__globals__['__file__']
                    )
                )
            swag_path, swag_type = get_path_from_doc(full_doc)
            doc_filepath = os.path.join(obj.root_path, swag_path)
            full_doc = load_from_file(doc_filepath, swag_type)

        line_feed = full_doc.find('\n')
        if line_feed != -1:
            first_line = process_doc(full_doc[:line_feed])
            yaml_sep = full_doc[line_feed + 1:].find('---')
            if yaml_sep != -1:
                other_lines = process_doc(
                    full_doc[line_feed + 1: line_feed + yaml_sep]
                )
                swag = yaml.load(full_doc[line_feed + yaml_sep:])
            else:
                other_lines = process_doc(full_doc[line_feed + 1:])
        else:
            first_line = full_doc

    return first_line, other_lines, swag


def _parse_definition_docstring(obj, process_doc):
    doc_lines, swag = None, None

    full_doc = None
    swag_path = getattr(obj, 'swag_path', None)
    swag_type = getattr(obj, 'swag_type', 'yml')

    if swag_path is not None:
        full_doc = load_from_file(swag_path, swag_type)
    else:
        full_doc = inspect.getdoc(obj)

    if full_doc:

        if full_doc.startswith('file:'):
            if not hasattr(obj, 'root_path'):
                obj.root_path = os.path.dirname(os.path.abspath(
                        obj.__globals__['__file__']
                    )
                )
            swag_path, swag_type = get_path_from_doc(full_doc)
            doc_filepath = os.path.join(obj.root_path, swag_path)
            full_doc = load_from_file(doc_filepath, swag_type)

        yaml_sep = full_doc.find('---')
        if yaml_sep != -1:
            doc_lines = process_doc(
                full_doc[:yaml_sep - 1]
            )
            swag = yaml.load(full_doc[yaml_sep:])
        else:
            doc_lines = process_doc(full_doc)

    return doc_lines, swag


def _extract_definitions(alist, level=None, endpoint=None, verb=None):
    """
    Since we couldn't be bothered to register models elsewhere
    our definitions need to be extracted from the parameters.
    We require an 'id' field for the schema to be correctly
    added to the definitions list.
    """
    endpoint = endpoint or request.endpoint.lower()
    verb = verb or request.method.lower()
    endpoint = endpoint.replace('.', '_')

    def _extract_array_defs(source):
        # extract any definitions that are within arrays
        # this occurs recursively
        ret = []
        items = source.get('items')
        if items is not None and 'schema' in items:
            ret += _extract_definitions([items], level + 1, endpoint, verb)
        return ret

    # for tracking level of recursion
    if level is None:
        level = 0

    defs = list()
    if alist is not None:
        for item in alist:
            if not getattr(item, 'get'):
                raise RuntimeError('definitions must be a list of dicts')
            schema = item.get("schema")
            if schema is not None:
                schema_id = schema.get("id")
                if schema_id is not None:
                    # add endpoint_verb to schema id to avoid conflicts
                    # schema['id'] = schema_id = "{}_{}_{}".format(endpoint,
                    #                                              verb,
                    #                                              schema_id)
                    # ^ removed for compliance with swagger specs

                    defs.append(schema)
                    ref = {"$ref": "#/definitions/{}".format(schema_id)}
                    # only add the reference as a schema if we are in a
                    # response or
                    # a parameter i.e. at the top level
                    # directly ref if a definition is used within another
                    # definition
                    if level == 0:
                        item['schema'] = ref
                    else:
                        item.update(ref)
                        del item['schema']

                # extract any definitions that are within properties
                # this occurs recursively
                properties = schema.get('properties')
                if properties is not None:
                    defs += _extract_definitions(
                        properties.values(), level + 1, endpoint, verb
                    )

                defs += _extract_array_defs(schema)

            defs += _extract_array_defs(item)

    return defs


class APIDocsView(MethodView):
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        super(APIDocsView, self).__init__(*args, **kwargs)

    def get(self):
        base_endpoint = self.config.get('endpoint', 'flasgger')
        specs = [
            {
                "url": url_for(".".join((base_endpoint, spec['endpoint']))),
                "title": spec.get('title'),
                "version": spec.get("version"),
                "endpoint": spec.get('endpoint')
            }
            for spec in self.config.get('specs', [])
        ]
        data = {
            "specs": specs,
            "title": self.config.get('title', 'Flasgger')
        }
        if request.args.get('json'):
            return jsonify(data)
        else:
            return render_template(
                'flasgger/index.html',
                **data
            )


def has_valid_dispatch_view_docs(endpoint):
    klass = endpoint.__dict__.get('view_class', None)
    return klass and hasattr(klass, 'dispatch_request') \
        and hasattr(endpoint, 'methods') \
        and getattr(klass, 'dispatch_request').__doc__


def is_valid_method_view(endpoint):
    klass = endpoint.__dict__.get('view_class', None)
    try:
        return issubclass(klass, MethodView)
    except TypeError:
        return False


class APISpecsView(MethodView):
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        self.spec = view_args.get('spec')
        self.process_doc = view_args.get('sanitizer', BR_SANITIZER)
        self.template = view_args.get('template')
        self.definition_models = view_args.get('definition_models')
        super(APISpecsView, self).__init__(*args, **kwargs)

    def get_url_mappings(self, rule_filter=None):
        rule_filter = rule_filter or (lambda rule: True)
        app_rules = [
            rule for rule in current_app.url_map.iter_rules()
            if rule_filter(rule)
        ]
        return app_rules

    def get_def_models(self, definition_filter=None):
        model_filter = definition_filter or (lambda tag: True)
        return {
            definition.name: definition.obj
            for definition in self.definition_models
            if model_filter(definition)
        }

    def get(self):
        data = {
            "swagger": self.config.get('swagger') or self.config.get(
                'swagger_version', "2.0"
            ),
            "info": self.config.get('info') or {
                "version": self.spec.get('version', "0.0.1"),
                "title": self.spec.get('title', "A swagger API"),
                "description": self.spec.get('description',
                                             "API description"),
                "termsOfService": self.spec.get('termsOfService',
                                                "Terms of service"),
            },
            "paths": self.config.get('paths') or defaultdict(dict),
            "definitions": self.config.get('definitions') or defaultdict(dict)
        }

        if self.config.get('host'):
            data['host'] = self.config.get('host')
        if self.config.get("basePath"):
            data["basePath"] = self.config.get('basePath')
        if self.config.get("securityDefinitions"):
            data["securityDefinitions"] = self.config.get(
                'securityDefinitions'
            )
        # set defaults from template
        if self.template is not None:
            data.update(self.template)

        paths = data['paths']
        definitions = data['definitions']
        ignore_verbs = set(
            self.config.get('ignore_verbs', ("HEAD", "OPTIONS"))
        )

        # technically only responses is non-optional
        optional_fields = [
            'tags', 'consumes', 'produces', 'schemes', 'security',
            'deprecated', 'operationId', 'externalDocs'
        ]

        for name, def_model in self.get_def_models(
                self.spec.get('definition_filter')).items():
            description, swag = _parse_definition_docstring(
                def_model, self.process_doc)
            if name and swag:
                if description:
                    swag.update({'description': description})
                definitions[name].update(swag)

        for rule in self.get_url_mappings(self.spec.get('rule_filter')):
            endpoint = current_app.view_functions[rule.endpoint]
            methods = dict()
            is_mv = is_valid_method_view(endpoint)
            for verb in rule.methods.difference(ignore_verbs):
                if not is_mv and has_valid_dispatch_view_docs(endpoint):
                    endpoint.methods = endpoint.methods or ['GET']
                    if verb in endpoint.methods:
                        methods[verb.lower()] = endpoint
                elif hasattr(endpoint, 'methods') and verb in endpoint.methods:
                    verb = verb.lower()
                    methods[verb] = getattr(endpoint.view_class, verb)
                else:
                    methods[verb.lower()] = endpoint
            operations = dict()
            for verb, method in methods.items():
                klass = method.__dict__.get('view_class', None)
                if not is_mv and klass and hasattr(klass, 'verb'):
                    method = klass.__dict__.get('verb')
                elif klass and hasattr(klass, 'dispatch_request'):
                    method = klass.__dict__.get('dispatch_request')
                if method is None:  # for method view
                    method = klass.__dict__.get(verb)
                summary, description, swag = _parse_docstring(
                    method, self.process_doc, endpoint=rule.endpoint, verb=verb
                )
                # we only add swagged endpoints
                if swag is not None:
                    definitions.update(swag.get('definitions', {}))
                    defs = []  # swag.get('definitions', [])
                    defs += _extract_definitions(
                        defs, endpoint=rule.endpoint, verb=verb)

                    params = swag.get('parameters', [])
                    defs += _extract_definitions(params,
                                                 endpoint=rule.endpoint,
                                                 verb=verb)

                    responses = swag.get('responses', {})
                    responses = {
                        str(key): value
                        for key, value in responses.items()
                    }
                    if responses is not None:
                        defs = defs + _extract_definitions(
                            responses.values(),
                            endpoint=rule.endpoint,
                            verb=verb
                        )
                    for definition in defs:
                        if 'id' not in definition:
                            definitions.update(definition)
                            continue
                        def_id = definition.pop('id')
                        if def_id is not None:
                            definitions[def_id].update(definition)
                    operation = dict(
                        summary=summary,
                        description=description,
                        responses=responses
                    )
                    # parameters - swagger ui dislikes empty parameter lists
                    if len(params) > 0:
                        operation['parameters'] = params
                    # other optionals
                    for key in optional_fields:
                        if key in swag:
                            operation[key] = swag.get(key)
                    operations[verb] = operation

            if len(operations):
                rule = str(rule)
                # old regex '(<(.*?\:)?(.*?)>)'
                for arg in re.findall('(<([^<>]*:)?([^<>]*)>)', rule):
                    rule = rule.replace(arg[0], '{%s}' % arg[2])
                paths[rule].update(operations)
        return jsonify(data)


class SwaggerDefinition(object):
    def __init__(self, name, obj, tags=None):
        self.name = name
        self.obj = obj
        self.tags = tags or []


class Swagger(object):

    DEFAULT_CONFIG = {
        "headers": [
        ],
        "specs": [
            {
                "version": "1.0.1",
                "title": "A swagger API",
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        # "static_folder": "static",  # must be set ny user
        "specs_route": "/apidocs/"
    }

    def __init__(self, app=None, config=None, sanitizer=None, template=None):
        self.endpoints = []
        self.definition_models = []  # not in app, so track here
        self.sanitizer = sanitizer or BR_SANITIZER
        self.config = config or self.DEFAULT_CONFIG.copy()
        self.template = template
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.load_config(app)
        self.register_views(app)
        self.add_headers(app)

    def definition(self, name, tags=None):
        def wrapper(obj):
            self.definition_models.append(SwaggerDefinition(name, obj,
                                                            tags=tags))
            return obj
        return wrapper

    def load_config(self, app):
        self.config.update(app.config.get('SWAGGER', {}))

    def register_views(self, app):
        uiversion = self.config.get('uiversion', 2)
        blueprint = Blueprint(
            self.config.get('endpoint', 'flasgger'),
            __name__,
            url_prefix=self.config.get('url_prefix', None),
            subdomain=self.config.get('subdomain', None),
            template_folder=self.config.get(
                'template_folder', 'ui{0}/templates'.format(uiversion)
            ),
            static_folder=self.config.get(
                'static_folder', 'ui{0}/static'.format(uiversion)
            ),
            static_url_path=self.config.get('static_url_path', None)
        )
        for spec in self.config['specs']:
            self.endpoints.append(spec['endpoint'])
            blueprint.add_url_rule(
                spec['route'],
                spec['endpoint'],
                view_func=APISpecsView().as_view(
                    spec['endpoint'],
                    view_args=dict(
                        app=app, config=self.config,
                        spec=spec, sanitizer=self.sanitizer,
                        template=self.template,
                        definition_models=self.definition_models
                    )
                )
            )

        blueprint.add_url_rule(
            self.config.get('specs_route', '/apidocs/'),
            'apidocs',
            view_func=APIDocsView().as_view(
                'spidocs',
                view_args=dict(config=self.config)
            )
        )

        # backwards compatibility with old url style
        blueprint.add_url_rule(
            '/apidocs/index.html',
            view_func=lambda: redirect(url_for('flasgger.apidocs'))
        )

        app.register_blueprint(blueprint)

    def add_headers(self, app):
        @app.after_request
        def after_request(response):  # noqa
            for header, value in self.config.get('headers'):
                response.headers[header] = value
            return response
