"""0.9.0 News and Changes

- Updated Swagger UI 3.x
- uiversion now defaults to 3
- 'hide_top_bar' config option to remove the green top bar
- 'fotter_text' added to customize the footer text (allows html and <script>)
- templates/flasgger/footer.html added and can be replaced to customization
  this footer.html is the right place for custom <script>
- 'top_text' added to customize the header text (allows html)
- templates/flasgger/top.html added and can be replaced to customization
- 'head_text' added to customize the <head> (allows html)
- templates/flasgger/head.html added and can be replaced to customization
- added 'doc_expansion' config to control the collapse
- added 'ui_params' to allow override of any swagger.ui values
"""

from flask import Flask, request
from flasgger import Swagger

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SWAGGER'] = {
    'title': 'MyAPI',

    # UI version 3 is now the default
    # 'uiversion': '3',

    # This setup hides the green top bar
    'hide_top_bar': True,

    # this text is rendered in the footer
    # (optionally you can replace flasgger/footer.html template)
    'footer_text': '<b>Hello World </b><script>alert("Hello World!")</script>',

    # this text is rendered in the header
    # (optionally you can replace flasgger/header.html template)
    'top_text': '<b><span class="top_text">Welcome to my api </span></b>',

    # this text is rendered in the <head>
    # (optionally you can replace flasgger/head.html template)
    'head_text': '<style>.top_text{color: red;}</style>',

    # Control the collapse of each tag, '"none"' means all tags default closed
    # "none" - It'll Hide everything.
    # "list"- It'll expand/List all the operations only. (default)
    # "full" - It'll expand everything(Full expand as the name says).
    'doc_expansion': "list",

    # Allows overriding any of the uiparams
    # This is useful to override other stuff not provided by the above aliases
    'ui_params': {
        'apisSorter': 'alpha',
        'operationsSorter': 'alpha',
    }
}

Swagger(app)


@app.route('/', methods=['GET', 'POST'])
def main_route():
    """
    Test Endpoint
    ---
    tags:
        -   Test
    parameters:
        -   name: data
            in: formData
            required: True
            type: string
            description: data to send
    responses:
        200:
            description: data received successfully
        404:
            description: data not found in request form
    """
    if 'data' not in request.form.keys():
        return 'data not found in request form', 404
    return 'data received: ' + str(request.form['data'])


if __name__ == '__main__':
    app.run()
