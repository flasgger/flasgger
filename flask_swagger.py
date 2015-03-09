"""
What's the big idea?

An endpoint that traverses all restful endpoints producing a swagger 2.0 schema
If a swagger yaml description is found in the docstrings for an endpoint
we add the endpoint to swagger specification output

"""
import inspect
import yaml
import re


def _sanitize(comment):
    return comment.replace('\n', '<br/>') if comment else comment


def _parse_docstring(obj):
    first_line, other_lines, swag = None, None, None
    full_doc = inspect.getdoc(obj)
    if full_doc:
        line_feed = full_doc.find('\n')
        if line_feed != -1:
            first_line = _sanitize(full_doc[:line_feed])
            yaml_sep = full_doc[line_feed+1:].find('---')
            if yaml_sep != -1:
                other_lines = _sanitize(full_doc[line_feed+1:line_feed+yaml_sep])
                swag = yaml.load(full_doc[line_feed+yaml_sep:])
            else:
                other_lines = _sanitize(full_doc[line_feed+1:])
        else:
            first_line = full_doc
    return first_line, other_lines, swag


def _extract_definitions(alist):
    """
    Since we couldn't be bothered to register models elsewhere
    our definitions need to be extracted from the parameters.
    We require a 'name' field for the schema to be correctly
    added to the definitions list.
    """

    defs = list()
    if alist is not None:
        for params in alist:
            schema = params.get("schema")
            if schema is not None:
                schema_id = schema.get("id")
                if schema_id is not None:
                    defs.append(schema)
                    params['schema'] = {
                        "$ref": "#/definitions/{}".format(schema_id)
                    }
    return defs


def swagger(app):
    """
    Call this from an @app.route method like this
    @app.route('/spec.json')
    def spec():
       return jsonify(swagger(app))

    We go through all endpoints of the app searching for swagger endpoints
    We provide the minimum required data according to swagger specs
    Callers can and should add and override at will
    """

    output = {
        "swagger": "2.0",
        "info": {
            "version": "0.0.0",
            "title": "Cool product name",
        },
        "paths": dict(),
        "definitions": dict()
    }

    paths = output['paths']
    definitions = output['definitions']
    ignore_verbs = {"HEAD", "OPTIONS"}
    # technically only responses is non-optional
    optional_fields = ['tags', 'consumes', 'produces', 'schemes', 'security',
                       'deprecated', 'operationId', 'externalDocs']

    for rule in app.url_map.iter_rules():
        endpoint = app.view_functions[rule.endpoint]
        methods = dict()
        if hasattr(endpoint, 'methods'):
            for verb in endpoint.methods:
                verb = verb.lower()
                methods[verb.lower()] = endpoint.view_class.__dict__.get(verb)
        else:
            for verb in rule.methods.difference(ignore_verbs):
                methods[verb.lower()] = endpoint
        operations = dict()
        for verb, method in methods.iteritems():
            summary, description, swag = _parse_docstring(method)
            if swag is not None:  # we only add endpoints with swagger data in the docstrings
                params = swag.get('parameters', [])
                defs = _extract_definitions(params)
                responses = swag.get('responses', {})
                if responses is not None:
                    defs = defs + _extract_definitions(responses.values())
                for definition in defs:
                    def_id = definition.get('id')
                    if def_id is not None:
                        definitions[def_id] = definition
                operation = dict(
                    summary=summary,
                    description=description,
                    parameters=params,
                    responses=responses
                )
                # optionals
                for key in optional_fields:
                    if key in swag:
                        operation[key] = swag.get(key)
                operations[verb] = operation

        if len(operations):
            rule = str(rule)
            for arg in re.findall('(<(.*?\:)?(.*?)>)', rule):
                rule = rule.replace(arg[0], '{%s}' % arg[2])
            paths[rule] = operations
    return output
