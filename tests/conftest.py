from importlib.util import find_spec

pytest_plugins = "pytester"

# if responses or respx are loaded, ignore basic cases
if (find_spec("responses") is not None) or (find_spec("respx") is not None):
    collect_ignore_glob = ["basic cases/*"]
