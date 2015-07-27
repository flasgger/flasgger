try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

setup(name='flasgger',
      version='0.2.8',
      url='https://github.com/rochacbruno/flasgger',
      description='Extract swagger specs from your flask project',
      author='Bruno Rocha',
      license='MIT',
      py_modules=['flasgger'],
      long_description=long_description,
      install_requires=['Flask>=0.10', 'PyYAML>=3.0'])
