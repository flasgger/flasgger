from packaging import version


def get_flask_version() -> version.Version:
    import flask
    try:
        v_str = flask.__version__
    except AttributeError:
        import pkg_resources  # noqa
        v_str = pkg_resources.get_distribution('flask').version  # noqa
    return version.parse(v_str)


flask_version = get_flask_version()


def get_python_version() -> version.Version:
    import platform
    return version.parse(platform.python_version())


python_version = get_python_version()

v = version.parse

# if __name__ == "__main__":
#     print(python_version)
