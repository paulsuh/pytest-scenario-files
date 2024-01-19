import os
from json import load
from os.path import join
from typing import Any

from yaml import safe_load


class BadTestCaseData(Exception):
    """A custom exception class for representing bad test case data.

    This class is used to indicate an error in the provided test case data. It is typically raised when the data provided for a test case is invalid or inconsistent.
    """

    pass


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
            raise BadTestCaseData(f"{filepath} did not produce a dictionary when loaded.")

        for case_name, case_data in test_data.values():
            if not isinstance(case_data, dict):
                raise BadTestCaseData(f"From {filepath}: data for case {case_name} is not a dict. ")

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

    fixture_raw_data_dict = {}
    for root, dirs, files in os.walk(os.getcwd()):
        # remove dirs that start with .
        for one_dir in dirs:
            if one_dir.startswith("."):
                dirs.remove(one_dir)

        test_data_filenames = [one_filename for one_filename in files if one_filename.startswith("data_" + test_name)]

        for one_data_file in test_data_filenames:
            test_data = _load_test_data_from_file(join(root, one_data_file))
            fixture_raw_data_dict |= test_data

    # check that all of the test cases have the same sets of keys
    all_fixture_keys = {
        one_fixture_name for test_case in fixture_raw_data_dict.values() for one_fixture_name in test_case.values()
    }

    bad_test_cases = {
        test_case_id: problem_keys
        for test_case_id, test_case_data in fixture_raw_data_dict
        if len(problem_keys := all_fixture_keys ^ set(test_case_data.keys())) > 0
    }

    if len(bad_test_cases) > 0:
        raise BadTestCaseData(f"Mismatched fixture keys {bad_test_cases}")

    fixture_names = sorted(all_fixture_keys)

    fixture_cases_dict = {
        test_case_id: {key: test_case_data[key] for key in sorted(fixture_raw_data_dict[test_case_id])}
        for test_case_id, test_case_data in fixture_raw_data_dict.items()
    }

    fixture_data_list = [test_case_values for test_case_values in fixture_cases_dict.values()]

    if len(fixture_raw_data_dict) > 0:
        metafunc.parametrize(fixture_names, fixture_data_list, ids=fixture_cases_dict.keys(), scope="function")
