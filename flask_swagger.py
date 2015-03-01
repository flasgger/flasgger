"""
What's the big idea?

An endpoint that traverses all restful endpoints producing a swagger 2.0 schema
If a swagger yaml description is found in the docstrings for an endpoint
we add the endpoint to swagger specification output

"""
import inspect
import yaml


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


def _extract_definitions(parameter_list):
    """
    Since we couldn't be bothered to register models elsewhere
    our definitions need to be extracted from the parameters.
    We require a 'name' field for the schema to be correctly
    added to the definitions list.
    """
    defs = list()
    for params in parameter_list:
        schema = params.get("schema")
        if schema is not None:
            schema_name = schema.get("name")
            if schema_name is not None:
                defs.append(schema)
                params['schema'] = {
                    "$ref": "#/definitions/{}".format(schema_name)
                }
    return parameter_list, defs


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

    for rule in app.url_map.iter_rules():
        endpoint = app.view_functions[rule.endpoint]
        if hasattr(endpoint, 'methods'):
            operations = dict()
            for verb in endpoint.methods:
                verb = verb.lower()
                method = endpoint.view_class.__dict__.get(verb)
                summary, description, swag = _parse_docstring(method)
                if swag is not None:  # we only add endpoints with swagger data in the docstrings
                    params, defs = _extract_definitions(swag.get('parameters', {}))
                    for definition in defs:
                        name = definition.get('name')
                        if name is not None:
                            definitions[name] = definition
                    operations[verb] = dict(
                        summary=summary,
                        description=description,
                        responses=swag.get('responses', {}),
                        tags=swag.get('tags', []),
                        parameters=params
                    )
            if len(operations):
                paths[str(rule)] = operations

    return output