# Fix for older setuptools
import logging
import re
import os

from setuptools import setup, find_packages, Command


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


def desc():
    return read('README.md')


# grep flasgger/__init__.py since python 3.x cannot
# import it before using 2to3
file_text = read(fpath('flasgger/__init__.py'))


def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, file_text)
    return strval


def download_swagger_ui(version: str = '3.52.5'):
    import tarfile
    import urllib.request
    url = f'https://registry.npmjs.org/swagger-ui-dist/-/swagger-ui-dist-{version}.tgz'
    destination = 'flasgger/ui3/static'

    import certifi

    # Create an SSL context with the specified CA certificate file
    import ssl
    context = ssl.create_default_context(cafile=certifi.where())

    with urllib.request.urlopen(url, context=context) as response:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(response.read())

            with tarfile.open(temp_file.name, 'r:gz') as tar:

                file_mappings = [
                    ('package/favicon-*', destination),
                    ('package/swagger-ui.css*', destination),
                    ('package/swagger-ui.js*', destination),
                    ('package/swagger-ui-standalone-preset.js*', destination),
                    ('package/swagger-ui-bundle.js*', destination),
                ]

                for pattern, dest_dir in file_mappings:
                    for member in tar.getmembers():

                        from fnmatch import fnmatch
                        if fnmatch(member.name, pattern):
                            member.name = member.name.lstrip('package/')
                            tar.extract(member, dest_dir)

    # # Cleanup: remove the downloaded tar file
    # os.remove(f'swagger-ui-dist-{version}.tgz')


from setuptools.command.install import install
from setuptools.command.develop import develop


class MixinSwaggerUiInstall:

    def _get_swagger_ui_version_string(self):
        # return '3.52.5'

        try:

            extras_require = self.distribution.extras_require
            version = None

            if 'swagger-ui' in extras_require:
                dependency = extras_require['swagger-ui'][0]
                match = re.match(r'swagger-ui==(\d+\.\d+)', dependency)
                if match:
                    version = match.group(1)

            return version
        except AttributeError:
            logging.exception('Failing to read swagger-ui version from extras_require')
            return None

    def run(self):
        super().run()
        # Your custom script logic goes here
        version = self._get_swagger_ui_version_string()
        # print("Running custom script during installation...")
        if version:
            logging.info(f"Running custom script during installation... swagger-ui=={version}")
            download_swagger_ui(version=version)


class SwaggerUiInstallCommand(MixinSwaggerUiInstall, install):
    pass


class SwaggerUiDevelopCommand(MixinSwaggerUiInstall, develop):
    pass


setup(
    name='flasgger',
    version=grep('__version__'),
    url='https://github.com/flasgger/flasgger/',
    license='MIT',
    author=grep('__author__'),
    author_email=grep('__email__'),
    description='Extract swagger specs from your flask project',
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
        'Flask>=0.10',
        'PyYAML>=3.0',
        'jsonschema>=3.0.1',
        'mistune',
        'six>=1.10.0',
        'packaging',
        'certifi',  # For downloading external dependencies such as swagger-ui
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
    extras_require={
        # 'swagger-ui': ['swagger-ui==3.28'],
    },
    cmdclass={
        'install': SwaggerUiInstallCommand,
        'develop': SwaggerUiDevelopCommand,
    },
)
