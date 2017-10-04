"""
What's the big idea?

An endpoint that traverses all restful endpoints producing a swagger 2.0 schema
If a swagger yaml description is found in the docstrings for an endpoint
we add the endpoint to swagger specification output

"""
import re
import os
import codecs
import yaml
try:
    import simplejson as json
except ImportError:
    import json
from functools import wraps
from collections import defaultdict
from flask import Blueprint
from flask import Markup
from flask import current_app
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request, url_for
from flask.views import MethodView
from flask.json import JSONEncoder
from mistune import markdown
from .constants import OPTIONAL_FIELDS
from .utils import extract_definitions
from .utils import get_specs
from .utils import get_schema_specs
from .utils import parse_definition_docstring
from .utils import get_vendor_extension_fields
from .utils import validate
from .utils import LazyString

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
                    'title', self.config.get('title', "A swagger API")
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

        specs = get_specs(
            self.get_url_mappings(self.spec.get('rule_filter')), ignore_verbs,
            optional_fields, self.process_doc)

        for rule, verbs in specs:
            operations = dict()
            for verb, swag in verbs:
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

                operation = {}
                if swag.get('summary'):
                    operation['summary'] = swag.get('summary')
                if swag.get('description'):
                    operation['description'] = swag.get('description')
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
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }

    def __init__(
            self, app=None, config=None, sanitizer=None, template=None,
            template_file=None, decorators=None, validation_function=None,
            validation_error_handler=None):
        self._configured = False
        self.endpoints = []
        self.definition_models = []  # not in app, so track here
        self.sanitizer = sanitizer or BR_SANITIZER
        self.config = config or self.DEFAULT_CONFIG.copy()
        self.template = template
        self.template_file = template_file
        self.decorators = decorators
        self.validation_function = validation_function
        self.validation_error_handler = validation_error_handler
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

        # Wrap the views in an arbitrary number of decorators.
        def wrap_view(view):
            if self.decorators:
                for decorator in self.decorators:
                    view = decorator(view)
            return view

        if self.config.get('swagger_ui', True):
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

            blueprint.add_url_rule(
                self.config.get('specs_route', '/apidocs/'),
                'apidocs',
                view_func=wrap_view(APIDocsView().as_view(
                    'apidocs',
                    view_args=dict(config=self.config)
                ))
            )

            # backwards compatibility with old url style
            blueprint.add_url_rule(
                '/apidocs/index.html',
                view_func=lambda: redirect(url_for('flasgger.apidocs'))
            )
        else:
            blueprint = Blueprint(
                self.config.get('endpoint', 'flasgger'),
                __name__
            )

        for spec in self.config['specs']:
            self.endpoints.append(spec['endpoint'])
            blueprint.add_url_rule(
                spec['route'],
                spec['endpoint'],
                view_func=wrap_view(APISpecsView().as_view(
                    spec['endpoint'],
                    view_args=dict(
                        app=app, config=self.config,
                        spec=spec, sanitizer=self.sanitizer,
                        template=self.template,
                        definition_models=self.definition_models
                    )
                ))
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

    def validate(
            self, schema_id, validation_function=None,
            validation_error_handler=None):
        """
        A decorator that is used to validate incoming requests data
        against a schema

            swagger = Swagger(app)

            @app.route('/pets', methods=['POST'])
            @swagger.validate('Pet')
            @swag_from("pet_post_endpoint.yml")
            def post():
                return db.insert(request.data)

        This annotation only works if the endpoint is already swagged,
        i.e. placing @swag_from above @validate or not declaring the
        swagger specifications in the method's docstring *won't work*

        Naturally, if you use @app.route annotation it still needs to
        be the outermost annotation

        :param schema_id: the id of the schema with which the data will
            be validated

        :param validation_function: custom validation function which
            takes the positional arguments: data to be validated at
            first and schema to validate against at second

        :param validation_error_handler: custom function to handle
            exceptions thrown when validating which takes the exception
            thrown as the first, the data being validated as the second
            and the schema being used to validate as the third argument
        """

        if validation_function is None:
            validation_function = self.validation_function

        if validation_error_handler is None:
            validation_error_handler = self.validation_error_handler

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                specs = get_schema_specs(schema_id, self)
                validate(
                    schema_id=schema_id, specs=specs,
                    validation_function=validation_function,
                    validation_error_handler=validation_error_handler)
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def get_schema(self, schema_id):
        """
        This method finds a schema known to Flasgger and returns it.

        :raise KeyError: when the specified :param schema_id: is not
        found by Flasgger

        :param schema_id: the id of the desired schema
        """
        schema_specs = get_schema_specs(schema_id, self)

        if schema_specs is None:
            raise KeyError('Specified schema_id \'{0}\' not found')

        for schema in (
                parameter.get('schema') for parameter in
                schema_specs['parameters']):
            if schema is not None and schema.get('id').lower() == schema_id:
                return schema


# backwards compatibility
Flasgger = Swagger  # noqa


class LazyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, LazyString):
            return str(obj)
        return super(LazyJSONEncoder, self).default(obj)
