import os
from json import load
from os.path import join
from typing import Any

from yaml import safe_load


class BadTestCaseDataException(Exception):
    """An exception class used to mark bad test case data."""

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
    """Load test data from a file and return it as a dictionary.

    :param filepath: The path of the file to load.
    :type filepath: str
    :return: The loaded test data as a dictionary.
    :rtype: dict[str, Any]
    :raises BadTestCaseDataException: If the loaded test case data are of the incorrect format.
    """
    with open(filepath) as fp:
        if filepath.endswith(".json"):
            test_data = load(fp)
        elif filepath.endswith((".yaml", ".yml")):
            test_data = safe_load(fp)
        else:
            raise BadTestCaseDataException(f"{filepath} does not have an extension of .json, .yaml, or .yml.")

        if not isinstance(test_data, dict):
            raise BadTestCaseDataException(f"{filepath} did not produce a dictionary when loaded.")

        for case_name, case_data in test_data.items():
            if not isinstance(case_data, dict):
                raise BadTestCaseDataException(f"From {filepath}: data for test case {case_name} is not a dict. ")

        _load_referenced_data(test_data)

        return test_data


def _load_referenced_data(base_data_dict: dict[str, dict[str, Any]]) -> None:
    """Load data for fixtures that refer to fixtures in other files.

    :param base_data_dict: A dictionary containing test cases and their fixtures.
    :return: None
    """
    for one_test_case in base_data_dict.values():
        for one_fixture_name, one_fixture_value in one_test_case.items():
            if isinstance(one_fixture_value, str):
                if one_fixture_value.startswith("__"):
                    data_file_path = one_fixture_value.removeprefix("__")
                    ref_data_file_name, ref_test_case, ref_fixture = data_file_path.split(":")
                    referenced_data_file_contents = _load_test_data_from_file(ref_data_file_name)
                    one_test_case[one_fixture_name] = referenced_data_file_contents[ref_test_case][ref_fixture]


def _locate_and_load_test_data(test_name: str, dir_name: str) -> dict[str, dict[str, Any]]:
    """Locates and loads test data for the given test name.

    :param test_name: The name of the test.
    :return: A dictionary containing the loaded test data.
    """
    return _locate_and_load_data_files("data_" + test_name, start_dir_path=dir_name)


def _locate_and_load_data_files(filename_base: str, start_dir_path: str = None) -> dict[str, dict[str, Any]]:
    """Locates and loads data for the given file name.

    :param filename_base: The root name of the files to be loaded.
    :type filename_base: str
    :param start_dir_path: path where to start the search for the data files
    :type start_dir_path: str
    :return: A dictionary containing the loaded data.
    :rtype: dict
    """
    if start_dir_path is None:
        start_dir_path = os.getcwd()
    result: dict[str, dict[str, Any]] = {}
    for root, dirs, files in os.walk(start_dir_path):
        # remove dirs that start with .
        for one_dir in dirs:
            if one_dir.startswith("."):
                dirs.remove(one_dir)

        test_data_filenames = [one_filename for one_filename in files if one_filename.startswith(filename_base)]

        for one_data_file in test_data_filenames:
            test_data = _load_test_data_from_file(join(root, one_data_file))
            _merge_new_test_data(result, test_data, one_data_file)

    return result


def _merge_new_test_data(
    result: dict[str, dict[str, Any]], new_test_data: dict[str, dict[str, Any]], new_data_file: str
) -> None:
    """Merge test case data from a new file into the existing set of test cases.

    :param result: A dictionary representing the result of merging the test data.
    :param new_test_data: A dictionary containing new test data to be merged.
    :param new_data_file: A string representing the file from which the new test data is loaded.
    :return: None
    :raises BadTestCaseDataException: raised if there is a conflict between data files for a given test case id and fixture
    """
    for new_test_case in new_test_data.keys():
        if result.get(new_test_case) is None:
            # No existing test case with that id, just add it
            result[new_test_case] = new_test_data[new_test_case]
        else:
            # There is an existing test case with that id, try to merge
            existing_test_case = result[new_test_case]
            for new_fixture in new_test_data[new_test_case].keys():
                if existing_test_case.get(new_fixture) is None:
                    # No existing fixture, just merge
                    existing_test_case[new_fixture] = new_test_data[new_test_case][new_fixture]
                else:
                    # Fixture already defined, raise an exception
                    raise BadTestCaseDataException(
                        f"In file {new_data_file} for test case {new_test_case}, fixture {new_fixture} already loaded."
                    )


def _extract_fixture_names(fixture_dict: dict[str, dict[str, Any]]) -> list[str]:
    """Check fixture names for consistency between test cases

    If all of the fixture names are consistent, return a sorted list of fixture names

    :param fixture_dict: Dict of dicts containing test case data.
    :return: A list of fixture names sorted alphabetically.
    :raises BadTestCaseData: If the fixture keys are mismatched between the test cases.
    """
    # check that all of the test cases have the same sets of keys
    # get all of the keys from all of the test cases
    all_fixture_keys = {
        one_fixture_name for test_case in fixture_dict.values() for one_fixture_name in test_case.keys()
    }

    # find test cases where there are keys in one set but not the other
    bad_test_cases = {
        test_case_id: problem_keys
        for test_case_id, test_case_data in fixture_dict.items()
        if len(problem_keys := all_fixture_keys ^ set(test_case_data.keys())) > 0
    }

    # raise an exception if there are bad test cases
    if len(bad_test_cases) > 0:
        raise BadTestCaseDataException(f"Mismatched fixture keys {bad_test_cases}")

    # return the list of fixture names sorted alphabetically
    return sorted(all_fixture_keys)


def _extract_fixture_data(fixture_raw_data_dict: dict[str, dict[str, Any]]) -> tuple[list[str], list[list[Any]]]:
    """Extracts fixture data into a format ready for the parameterize call.

    metafunc.parameterize() expects a list of fixture names, a list of lists of data, and an optional list
    of case id's. _extract_fixture_names() gets the names, this function sets up the other two lists.

    :param fixture_raw_data_dict: A dictionary containing fixture data, where the keys are test case IDs and the
                                  values are dictionaries mapping fixture names to fixture data.
    :type fixture_raw_data_dict: dict[str, dict[str, Any]]
    :return: A tuple containing the list of test case IDs and a list of lists representing the fixture data.
    :rtype: tuple[list[str], list[list[Any]]]
    """
    # this sets up a dict of dicts by case id, with the keys of each sub-dict being the
    # fixture names in alphabetical order
    fixture_cases_dict = {
        test_case_id: {key: test_case_data[key] for key in sorted(fixture_raw_data_dict[test_case_id])}
        for test_case_id, test_case_data in fixture_raw_data_dict.items()
    }
    # derive a list of lists from the dict of dicts. It's important to do this
    # so that the lists are in the same order as the case id's
    fixture_data_list = [
        [test_case_values for test_case_values in test_case.values()] for test_case in fixture_cases_dict.values()
    ]
    return list(fixture_cases_dict.keys()), fixture_data_list


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
    test_file_dir = metafunc.definition.path.parent

    fixture_raw_data_dict = _locate_and_load_test_data(test_name, test_file_dir)

    if len(fixture_raw_data_dict) > 0:
        # do processing only if the search found cases

        # get the list of fixture names sorted alphabetically
        # will raise an exception if the fixture names are inconsistent
        fixture_names = _extract_fixture_names(fixture_raw_data_dict)

        # reformat the case ids and fixture data into list and list of lists respectively
        case_ids, fixture_data_list = _extract_fixture_data(fixture_raw_data_dict)

        # do the parameterization
        metafunc.parametrize(fixture_names, fixture_data_list, ids=case_ids, scope="function")
