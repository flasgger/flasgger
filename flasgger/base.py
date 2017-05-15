"""
What's the big idea?

An endpoint that traverses all restful endpoints producing a swagger 2.0 schema
If a swagger yaml description is found in the docstrings for an endpoint
we add the endpoint to swagger specification output

"""
import re
import os
import codecs
try:
    import simplejson as json
except ImportError:
    import json
import yaml
from collections import defaultdict
from copy import deepcopy

from flask import (Blueprint, Markup, current_app, jsonify, redirect,
                   render_template, request, url_for)
from flask.views import MethodView
from mistune import markdown

from flasgger.constants import OPTIONAL_FIELDS
from flasgger.marshmallow_apispec import SwaggerView, convert_schemas
from flasgger.utils import (extract_definitions, has_valid_dispatch_view_docs,
                            is_valid_method_view, parse_definition_docstring,
                            parse_docstring, get_vendor_extension_fields)

NO_SANITIZER = lambda text: text  # noqa
BR_SANITIZER = lambda text: text.replace('\n', '<br/>') if text else text  # noqa
MK_SANITIZER = lambda text: Markup(markdown(text)) if text else text  # noqa


class APIDocsView(MethodView):
    """
    The /apidocs
    """
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        super(APIDocsView, self).__init__(*args, **kwargs)

    def get(self):
        """
        The data under /apidocs
        json or Swagger UI
        """
        base_endpoint = self.config.get('endpoint', 'flasgger')
        specs = [
            {
                "url": url_for(".".join((base_endpoint, spec['endpoint']))),
                "title": spec.get('title', 'API Spec 1'),
                "version": spec.get("version", '0.0.1'),
                "endpoint": spec.get('endpoint')
            }
            for spec in self.config.get('specs', [])
        ]
        data = {
            "specs": specs,
            "title": self.config.get('title', 'Flasgger')
        }
        if request.args.get('json'):
            # calling with ?json returns specs
            return jsonify(data)
        else:  # pragma: no cover
            return render_template(
                'flasgger/index.html',
                **data
            )


class APISpecsView(MethodView):
    """
    The /apispec_1.json and other specs
    """
    def __init__(self, *args, **kwargs):
        view_args = kwargs.pop('view_args', {})
        self.config = view_args.get('config')
        self.spec = view_args.get('spec')
        self.process_doc = view_args.get('sanitizer', BR_SANITIZER)
        self.template = view_args.get('template')
        self.definition_models = view_args.get('definition_models')
        super(APISpecsView, self).__init__(*args, **kwargs)

    def get_url_mappings(self, rule_filter=None):
        """
        Returns all werkzeug rules
        """
        rule_filter = rule_filter or (lambda rule: True)
        app_rules = [
            rule for rule in current_app.url_map.iter_rules()
            if rule_filter(rule)
        ]
        return app_rules

    def get_def_models(self, definition_filter=None):
        """
        Used for class based definitions
        """
        model_filter = definition_filter or (lambda tag: True)
        return {
            definition.name: definition.obj
            for definition in self.definition_models
            if model_filter(definition)
        }

    def get(self):
        """
        The Swagger view get method outputs to /apispecs_1.json
        """
        data = {
            "swagger": self.config.get('swagger') or self.config.get(
                'swagger_version', "2.0"
            ),
            # try to get from config['SWAGGER']['info']
            # then config['SWAGGER']['specs'][x]
            # then config['SWAGGER']
            # then default
            "info": self.config.get('info') or {
                "version": self.spec.get(
                    'version', self.config.get('version', "0.0.1")
                ),
                "title": self.spec.get(
                    'title', self.config.get('title', "A swagger API 2")
                ),
                "description": self.spec.get(
                    'description', self.config.get('description',
                                                   "powered by Flasgger")
                ),
                "termsOfService": self.spec.get(
                    'termsOfService', self.config.get('termsOfService',
                                                      "/tos")
                ),
            },
            "paths": self.config.get('paths') or defaultdict(dict),
            "definitions": self.config.get('definitions') or defaultdict(dict)
        }

        # Support extension properties in the top level config
        top_level_extension_options = get_vendor_extension_fields(self.config)
        if top_level_extension_options:
            data.update(top_level_extension_options)

        # if True schemaa ids will be prefized by function_method_{id}
        # for backwards compatibility with <= 0.5.14
        prefix_ids = self.config.get('prefix_ids')

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
        optional_fields = self.config.get('optional_fields') or OPTIONAL_FIELDS

        for name, def_model in self.get_def_models(
                self.spec.get('definition_filter')).items():
            description, swag = parse_definition_docstring(
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
                elif getattr(endpoint, 'methods', None) is not None:
                    if verb in endpoint.methods:
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
                if method is None:  # for MethodView
                    method = klass.__dict__.get(verb)

                if method is None:
                    if is_mv:  # #76 Empty MethodViews
                        continue
                    raise RuntimeError(
                        'Cannot detect view_func for rule {0}'.format(rule)
                    )

                swag = {}
                swagged = False

                view_class = getattr(endpoint, 'view_class', None)
                if view_class and issubclass(view_class, SwaggerView):
                    apispec_swag = {}
                    apispec_attrs = optional_fields + [
                        'parameters', 'definitions', 'responses',
                        'summary', 'description'
                    ]
                    for attr in apispec_attrs:
                        value = getattr(view_class, attr)
                        if value:
                            apispec_swag[attr] = value

                    apispec_definitions = apispec_swag.get('definitions', {})
                    swag.update(
                        convert_schemas(apispec_swag, apispec_definitions)
                    )

                    swagged = True

                if getattr(method, 'specs_dict', None):
                    swag.update(deepcopy(method.specs_dict))
                    swagged = True

                doc_summary, doc_description, doc_swag = parse_docstring(
                    method, self.process_doc,
                    endpoint=rule.endpoint, verb=verb
                )
                if doc_swag:
                    swag.update(doc_swag or {})
                    swagged = True

                # we only add swagged endpoints
                if swagged:
                    if doc_summary:
                        swag['summary'] = doc_summary
                    if doc_description:
                        swag['description'] = doc_description

                    definitions.update(swag.get('definitions', {}))
                    defs = []  # swag.get('definitions', [])
                    defs += extract_definitions(
                        defs, endpoint=rule.endpoint, verb=verb,
                        prefix_ids=prefix_ids
                    )

                    params = swag.get('parameters', [])
                    defs += extract_definitions(params,
                                                endpoint=rule.endpoint,
                                                verb=verb,
                                                prefix_ids=prefix_ids)

                    responses = None
                    if 'responses' in swag:
                        responses = swag.get('responses', {})
                        responses = {
                            str(key): value
                            for key, value in responses.items()
                        }
                        if responses is not None:
                            defs = defs + extract_definitions(
                                responses.values(),
                                endpoint=rule.endpoint,
                                verb=verb,
                                prefix_ids=prefix_ids
                            )
                        for definition in defs:
                            if 'id' not in definition:
                                definitions.update(definition)
                                continue
                            def_id = definition.pop('id')
                            if def_id is not None:
                                definitions[def_id].update(definition)

                    operation = dict(
                        summary=swag.get('summary'),
                        description=swag.get('description'),
                    )

                    if responses:
                        operation['responses'] = responses
                    # parameters - swagger ui dislikes empty parameter lists
                    if len(params) > 0:
                        operation['parameters'] = params
                    # other optionals
                    for key in optional_fields:
                        if key in swag:
                            value = swag.get(key)
                            if key in ('produces', 'consumes'):
                                if not isinstance(value, (list, tuple)):
                                    value = [value]

                            operation[key] = value
                    operations[verb] = operation

            if len(operations):
                srule = str(rule)
                # old regex '(<(.*?\:)?(.*?)>)'
                for arg in re.findall('(<([^<>]*:)?([^<>]*)>)', srule):
                    srule = srule.replace(arg[0], '{%s}' % arg[2])

                for key, val in operations.items():
                    if key in paths[srule]:
                        paths[srule][key].update(val)
                    else:
                        paths[srule][key] = val
        return jsonify(data)


class SwaggerDefinition(object):
    """
    Class based definition
    """
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
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,  # all in
                "model_filter": lambda tag: True,  # all in
            }
        ],
        "static_url_path": "/flasgger_static",
        # "static_folder": "static",  # must be set by user
        "specs_route": "/apidocs/"
    }

    def __init__(self, app=None, config=None,
                 sanitizer=None, template=None, template_file=None):
        self._configured = False
        self.endpoints = []
        self.definition_models = []  # not in app, so track here
        self.sanitizer = sanitizer or BR_SANITIZER
        self.config = config or self.DEFAULT_CONFIG.copy()
        self.template = template
        self.template_file = template_file
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize the app with Swagger plugin
        """
        self.app = app

        self.load_config(app)
        # self.load_apispec(app)
        if self.template_file is not None:
            self.template = self.load_swagger_file(self.template_file)
        self.register_views(app)
        self.add_headers(app)
        self._configured = True
        app.swag = self

    def load_swagger_file(self, filename):
        if not filename.startswith('/'):
            filename = os.path.join(
                self.app.root_path,
                filename
            )

        if filename.endswith('.json'):
            loader = json.load
        elif filename.endswith('.yml') or filename.endswith('.yaml'):
            loader = yaml.load
        else:
            with codecs.open(filename, 'r', 'utf-8') as f:
                contents = f.read()
                contents = contents.strip()
                if contents[0] in ['{', '[']:
                    loader = json.load
                else:
                    loader = yaml.load
        with codecs.open(filename, 'r', 'utf-8') as f:
            return loader(f)

    @property
    def configured(self):
        """
        Return if `init_app` is configured
        """
        return self._configured

    def definition(self, name, tags=None):
        """
        Decorator to add class based definitions
        """
        def wrapper(obj):
            self.definition_models.append(SwaggerDefinition(name, obj,
                                                            tags=tags))
            return obj
        return wrapper

    def load_config(self, app):
        """
        Copy config from app
        """
        self.config.update(app.config.get('SWAGGER', {}))

    def register_views(self, app):
        """
        Register Flasgger views
        """
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
        """
        Inject headers after request
        """
        @app.after_request
        def after_request(response):  # noqa
            for header, value in self.config.get('headers'):
                response.headers[header] = value
            return response


# backwards compatibility
Flasgger = Swagger  # noqa
