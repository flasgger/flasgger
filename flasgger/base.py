"""
What's the big idea?

An endpoint that traverses all restful endpoints producing a swagger 2.0 schema
If a swagger yaml description is found in the docstrings for an endpoint
we add the endpoint to swagger specification output

"""
import inspect
import yaml
import re
import os

from collections import defaultdict
from flask import jsonify, Blueprint, url_for, current_app, Markup, request
from flask.views import MethodView
from mistune import markdown

NO_SANITIZER = lambda text: text
BR_SANITIZER = lambda text: text.replace('\n', '<br/>') if text else text
MK_SANITIZER = lambda text: Markup(markdown(text)) if text else text


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

    try:
        return open(swag_path).read()
    except IOError:
        swag_path = os.path.join(os.path.dirname(__file__), swag_path)
        return open(swag_path).read()

    # TODO:
    # with open(swag_path) as swag_file:
    #     content = swag_file.read()
    #     if swag_type in ('yaml', 'yml'):
    #         return content
    #     elif swag_type  == 'json':
    #         return json_to_yaml(content)


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
            full_doc = load_from_file(*get_path_from_doc(full_doc))

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
            schema = item.get("schema")
            if schema is not None:
                schema_id = schema.get("id")
                if schema_id is not None:
                    # add endpoint_verb to schema id to avoid conflicts
                    schema['id'] = schema_id = "{}_{}_{}".format(endpoint,
                                                                 verb,
                                                                 schema_id)
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


class SpecsView(MethodView):
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        super(SpecsView, self).__init__(*args, **kwargs)

    def get(self):
        base_endpoint = self.config.get('endpoint', 'swagger')
        specs = [
            {
                "url": url_for(".".join((base_endpoint, spec['endpoint']))),
                "title": spec.get('title'),
                "version": spec.get("version"),
                "endpoint": spec.get('endpoint')
            }
            for spec in self.config.get('specs', [])
        ]
        return jsonify(
            {"specs": specs,
             "title": self.config.get('title', 'Flasgger')}
        )


def is_valid_dispatch_view(endpoint):
    klass = endpoint.__dict__.get('view_class', None)
    return klass and hasattr(klass, 'dispatch_request') \
        and hasattr(endpoint, 'methods')


class OutputView(MethodView):
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        self.spec = view_args.get('spec')
        self.process_doc = view_args.get('sanitizer', BR_SANITIZER)
        self.template = view_args.get('template')
        super(OutputView, self).__init__(*args, **kwargs)

    def get_url_mappings(self, rule_filter=None):
        rule_filter = rule_filter or (lambda rule: True)
        app_rules = [
            rule for rule in current_app.url_map.iter_rules()
            if rule_filter(rule)
        ]
        return app_rules

    def get(self):
        data = {
            "swagger": self.config.get('swagger_version', "2.0"),
            "info": {
                "version": self.spec.get('version', "0.0.0"),
                "title": self.spec.get('title', "A swagger API"),
                "description": self.spec.get('description',
                                             "API description"),
                "termsOfService": self.spec.get('termsOfService',
                                                "Terms of service"),
            },
            "paths": defaultdict(dict),
            "definitions": defaultdict(dict)
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
        ignore_verbs = set(("HEAD", "OPTIONS"))

        # technically only responses is non-optional
        optional_fields = [
            'tags', 'consumes', 'produces', 'schemes', 'security',
            'deprecated', 'operationId', 'externalDocs'
        ]

        for rule in self.get_url_mappings(self.spec.get('rule_filter')):
            endpoint = current_app.view_functions[rule.endpoint]
            methods = dict()
            for verb in rule.methods.difference(ignore_verbs):
                if is_valid_dispatch_view(endpoint):
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
                if klass and hasattr(klass, 'dispatch_request'):
                    method = klass.__dict__.get('dispatch_request')
                summary, description, swag = _parse_docstring(
                    method, self.process_doc, endpoint=rule.endpoint, verb=verb
                )
                # we only add endpoints with swagger data in the docstrings
                if swag is not None:
                    defs = swag.get('definitions', [])
                    defs = _extract_definitions(defs, endpoint=rule.endpoint,
                                                verb=verb)

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


class Swagger(object):

    DEFAULT_CONFIG = {
        "headers": [
        ],
        "specs": [
            {
                "version": "1.0.1",
                "title": "A swagger API",
                "endpoint": 'spec',
                "route": '/spec',
                "rule_filter": lambda rule: True  # all in
            }
        ],
        "static_url_path": "/apidocs",
        "static_folder": "swaggerui",
        "specs_route": "/specs"
    }

    def __init__(self, app=None, config=None, sanitizer=None, template=None):
        self.endpoints = []
        self.sanitizer = sanitizer or BR_SANITIZER
        self.config = config or self.DEFAULT_CONFIG.copy()
        self.template = template
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.load_config(app)
        self.register_views(app)
        self.add_headers(app)

    def load_config(self, app):
        self.config.update(app.config.get('SWAGGER', {}))

    def register_views(self, app):
        blueprint = Blueprint(
            self.config.get('endpoint', 'swagger'),
            __name__,
            url_prefix=self.config.get('url_prefix', None),
            subdomain=self.config.get('subdomain', None),
            template_folder=self.config.get('template_folder', 'templates'),
            static_folder=self.config.get('static_folder', 'static'),
            static_url_path=self.config.get('static_url_path', None)
        )
        for spec in self.config['specs']:
            self.endpoints.append(spec['endpoint'])
            blueprint.add_url_rule(
                spec['route'],
                spec['endpoint'],
                view_func=OutputView().as_view(
                    spec['endpoint'],
                    view_args=dict(
                        app=app, config=self.config,
                        spec=spec, sanitizer=self.sanitizer,
                        template=self.template
                    )
                )
            )

        blueprint.add_url_rule(
            self.config.get('specs_route', '/specs'),
            'specs',
            view_func=SpecsView().as_view(
                'specs',
                view_args=dict(config=self.config)
            )
        )

        app.register_blueprint(blueprint)

    def add_headers(self, app):
        @app.after_request
        def after_request(response):  # noqa
            for header, value in self.config.get('headers'):
                response.headers[header] = value
            return response
