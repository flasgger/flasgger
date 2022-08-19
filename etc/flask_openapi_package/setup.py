try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


setup(
    name='flask_openapi_package',
    version='0.0.1',
    url='https://github.com/overflowdigital/Flask-OpenAPI/',
    license='MIT',
    author='Overflow Digital',
    author_email='team@overflow.digital',
    description='A package to use during local and CI tests',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'flasgger>=0.9.4.dev0',
    ]
)
