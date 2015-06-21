try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README') as file:
    long_description = file.read()

setup(name='flask-swagger',
      version='0.2.8',
      url='https://github.com/gangverk/flask-swagger',
      description='Extract swagger specs from your flask project',
      author='Atli Thorbjornsson',
      license='MIT',
      py_modules=['flask_swagger'],
      long_description=long_description,
      install_requires=['Flask>=0.10', 'PyYAML>=3.0'])
