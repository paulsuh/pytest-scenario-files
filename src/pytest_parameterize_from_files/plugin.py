import os
from json import load
from os.path import join
from typing import Any

from yaml import safe_load


def pytest_addoption(parser):
    """Called by Pytest to load this plug-in

    :param parser: parser used by Pytest
    """
    group = parser.getgroup("Parameterize from files plug-in")
    group.addoption(
        "--param-from-files",
        action="store_true",
        dest="parameterize_from_files",
        default=False,
        help="Parameterize unit tests with values loaded from files.",
    )


def _load_test_data_from_file(filepath: str) -> dict[str, Any]:
    with open(filepath) as fp:
        if filepath.endswith(".json"):
            test_data = load(fp)
        elif filepath.endswith((".yaml", ".yml")):
            test_data = safe_load(fp)

        if not isinstance(test_data, dict):
            raise RuntimeError(f"{filepath} did not produce a dictionary when loaded.")

        return test_data


def pytest_generate_tests(metafunc):
    """Hook called by Pytest for each test.

    This is where the heavy lifting is done. This walks the directory tree
    looking for files that match the name of the test. Any data are loaded
    and used to parameterize the test.

    :param metafunc: Pytest fixture used to create the parameterization
    """
    if not metafunc.config.option.parameterize_from_files:
        return

    # load up files in same or lower dirs that start with the same
    # name as the test function prefixed by data_
    # E.g.,
    # parameterize against list of names if match
    test_name = metafunc.definition.name.removeprefix("test_")

    fixture_data_dict = {}
    for root, dirs, files in os.walk(os.getcwd()):
        # remove dirs that start with .
        for one_dir in dirs:
            if one_dir.startswith("."):
                dirs.remove(one_dir)

        test_data_filenames = [one_filename for one_filename in files if one_filename.startswith("data_" + test_name)]

        for one_data_file in test_data_filenames:
            test_data = _load_test_data_from_file(join(root, one_data_file))
            fixture_data_dict |= test_data

    if len(fixture_data_dict) > 0:
        metafunc.parametrize(
            "paramfiledata", fixture_data_dict.values(), ids=fixture_data_dict.keys(), scope="function"
        )
