try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


setup(
    name='flasgger_package',
    version='0.0.1',
    url='https://github.com/rochacbruno/flasgger/',
    license='MIT',
    author='testing@flasgger',
    author_email='testing@flasgger',
    description='A package to use during local and CI tests',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'flasgger>=0.9.4.dev0',
    ]
)
