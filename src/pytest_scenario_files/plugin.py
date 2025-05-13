from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import AbstractContextManager, nullcontext
from json import load
from os.path import join
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, Union, cast

import pytest
from yaml import safe_load

if TYPE_CHECKING:
    from responses import RequestsMock
    from respx import MockResponse, MockRouter


# configuration flag holding space
class _PsfConfigTuple(NamedTuple):
    psf_load_responses: bool
    psf_fire_all_responses: bool
    psf_load_respx: bool
    psf_assert_all_called: bool
    psf_assert_all_mocked: bool


_config_keys = (
    ("psf-load-responses", "Automatically load data for Responses from scenario files"),
    ("psf-fire-all-responses", "Are all responses required to be fired (for Responses)?"),
    ("psf-load-respx", "Automatically load data for Respx from scenario files"),
    ("psf-assert-all-called", "Are all responses required to be fired (for Respx)?"),
    ("psf-assert-all-mocked", "Are all Httpx calls required to be mocked (for Respx)?"),
)


_psf_configs: _PsfConfigTuple


# Need to use a NamedTuple as the key for the routing dict
# Can't use a dict as a dict can't be a dict key (unless you
# do funky stuff to make it immutable).
class _RespxRouteKey(NamedTuple):
    method: str
    url: str


class BadTestCaseDataException(Exception):
    """An exception class used to mark bad test case data."""

    pass


def pytest_addoption(parser: pytest.Parser, pluginmanager):
    """
    Pytest hook function that adds the command line options.

    Adds the command line options to automatically load http responses for the Responses
    package or the Respx package and additional options whether to require all
    responses to be fired and all calls to be mocked.
    """
    option_group = parser.getgroup("Pytest Scenario Files", "Options for the pytest-scenario-files plug-in")
    for opt, help_text in _config_keys:
        option_group.addoption(
            f"--{opt}",
            action="store_true",
            default=False,
            dest=opt,
            help=help_text,
        )


def pytest_configure(config: pytest.Config):
    """Get config data from command line flags

    Raises an exception if both `--psf-load-responses` and `--psf-load-respx` are both
    enabled since these are mutually exclusive options. Also stores values for
    `psf-fire-all-responses`, `psf-assert-all-fired`, and `psf-assert-all-mocked`.

    :param config: The pytest configuration object containing all command-line
        options and plugin configuration.
    :type config: pytest.Config
    :raises pytest.UsageError: If both `--psf-load-responses` and `--psf-load-respx`
        options are specified simultaneously.
    """
    global _psf_configs
    _psf_configs = _PsfConfigTuple(*(config.getoption(opt) for opt, _ in _config_keys))
    if _psf_configs.psf_load_responses and _psf_configs.psf_load_respx:
        raise pytest.UsageError("The --psf-load-resposes and --psf-load-respx options are mutually exclusive.")


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
                    referenced_data_file_contents = _locate_and_load_data_files(ref_data_file_name, os.getcwd())
                    one_test_case[one_fixture_name] = referenced_data_file_contents[ref_test_case][ref_fixture]


def _locate_and_load_test_data(test_name: str, dir_name: str) -> dict[str, dict[str, Any]]:
    """Locates and loads test data for the given test name.

    :param test_name: The name of the test.
    :type test_name: str
    :param dir_name:
    :type dir_name: str
    :return: A dictionary containing the loaded test data.
    :rtype: dict
    """
    return _locate_and_load_data_files("data_" + test_name, dir_name)


def _locate_and_load_data_files(filename_base: str, dir_name: str) -> dict[str, dict[str, Any]]:
    """Locates and loads data for the given file name.

    This function is used by both _locate_and_load_test_data() and _load_referenced_data().

    :param filename_base: The root name of the files to be loaded.
    :type filename_base: str
    :param dir_name: path where to start the search for the data files
    :type dir_name: str
    :return: A dictionary containing the loaded data.
    :rtype: dict
    """
    # This could be more efficiently cached, as referenced files may be loaded many times.
    # However, the total time required seems to be relatively small even for a complex
    # set of over 100 tests, so we'll add that when it becomes necessary.
    result: dict[str, dict[str, Any]] = {}
    for root, dirs, files in os.walk(dir_name):
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
    :raises BadTestCaseDataException: raised if there is a conflict between data files for a given
            test case id and fixture
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


def _extract_indirect_fixtures(
    fixture_data_dict: dict[str, dict[str, Any]], all_fixture_names: list[str]
) -> tuple[list[str], Union[list[str], bool]]:  # noqa UP007    Allow old style Union for Python 3.9
    """Extracts indirect fixtures

    :param fixture_data_dict: A dictionary of fixture data after loading referenced fixtures.
    :param all_fixture_names: A list of all fixture names.
    :return: A tuple containing the list of all fixture names with any _indirect suffixes removed and either
             a list of indirect fixture names or False if there are no indirect fixtures (so that this
             value can be fed directly into metafunc.parameterize()).
    """
    indirect_fixtures = []
    all_fixtures_trimmed = []
    for fixture_name in all_fixture_names:
        if fixture_name.endswith("_indirect"):
            fixture_name = fixture_name.removesuffix("_indirect")
            indirect_fixtures.append(fixture_name)
        all_fixtures_trimmed.append(fixture_name)

    if len(indirect_fixtures) > 0:
        for one_test_case_data in fixture_data_dict.values():
            for one_fixture_name in indirect_fixtures:
                fixture_data = one_test_case_data.pop(one_fixture_name + "_indirect")
                one_test_case_data[one_fixture_name] = fixture_data

        return all_fixtures_trimmed, indirect_fixtures
    else:
        return all_fixtures_trimmed, False


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


@pytest.fixture(scope="function")
def psf_responses(request: pytest.FixtureRequest) -> Generator[RequestsMock, None, None]:
    """Returns a responses.RequestsMock with scenario data loaded.

    Used for integration with the Responses package. Each test scenario will get its
    own active RequestsMock object. This object can then be updated at runtime
    to override the responses loaded from files.
    """
    from responses import RequestsMock

    psf_fire_all_responses = _psf_configs.psf_fire_all_responses
    with RequestsMock(assert_all_requests_are_fired=psf_fire_all_responses) as rsps:
        for one_response in request.param:
            rsps.add(**one_response)
        yield rsps


@pytest.fixture(scope="function")
def psf_respx_mock(request: pytest.FixtureRequest) -> Generator[MockRouter, None, None]:
    """Returns a respx.MockRouter with scenario data loaded.

    Used for integration with the Respx package. Each test scenario will get its
    own active MockRouter object. This object can then be updated at runtime
    to override the responses loaded from files.
    """
    from respx import mock
    from respx.models import MockResponse

    with mock(
        assert_all_mocked=_psf_configs.psf_assert_all_mocked, assert_all_called=_psf_configs.psf_assert_all_called
    ) as respx_mock:
        #   work through the list of values for the psf_respx_mock fixture
        #   and transform them by sorting into a new dict of lists by route (method, url)
        routes_dict: dict[_RespxRouteKey, list[MockResponse]] = {}
        for one_response in request.param:
            mock_response_kwargs = cast(dict, one_response.copy())
            route_match_dict = {k: mock_response_kwargs.pop(k) for k in ("method", "url")}
            route_match = _RespxRouteKey(**route_match_dict)
            routes_dict.setdefault(route_match, list()).append(MockResponse(**mock_response_kwargs))
        # pass through the dict of routes and add them to the mock
        for one_route, one_result in routes_dict.items():
            # If there is only one, set up router return value = MockResponse
            # If three are multiple, set up router side effect = list of MockResponse
            if len(one_result) == 1:
                respx_mock.route(**one_route._asdict()).return_value = one_result[0]
            else:
                respx_mock.route(**one_route._asdict()).side_effect = one_result

        yield respx_mock


@pytest.fixture(scope="function")
def psf_expected_result(request: pytest.FixtureRequest) -> AbstractContextManager:
    """Convenience fixture for possible expected exceptions

    Pytest has a pattern called Parameterized Conditional Raising (See:
    https://docs.pytest.org/en/8.3.x/example/parametrize.html#parametrizing-conditional-raising).
    This fixture allows the user to specify either an expected exception (including
    a match string or regexp) in the scenario file, or any other expected result value.
    An exception gets wrapped in a pytest.raises() context manager, while any other
    value gets wrapped in a nullcontext() context manager. The test function can then
    use a call like::

        with psf_expected_result as expected_result:
            assert expected_result == function_being_tested()

    :param request: The fixture request object containing the test parameters.
    :type request: pytest.FixtureRequest
    :return: A context manager that either catches the expected exception or
        a nullcontext() context manager.
    :rtype: AbstractContextManager:
    """
    if isinstance(request.param, dict) and "expected_exception_name" in request.param:
        # expected result is an exception
        expected_exception_name = request.param.pop("expected_exception_name")
        if "." in expected_exception_name:
            # expected exception is defined in a module or package
            import importlib

            module_name, exception_class_name = expected_exception_name.rsplit(".", 1)
            module = importlib.import_module(module_name)
            exception_class = getattr(module, exception_class_name)
        else:
            # expected exception is a builtin
            exception_class = (globals()["__builtins__"][expected_exception_name],)

        # pytest.raises() has a deprecated legacy form where you pass in a callable
        # and it returns an ExceptionInfo object. Tell mypy to gnore this as we are
        # only using the form of the call that returns a context manager.
        return pytest.raises(exception_class, **request.param)  # type:ignore[return-value]

    else:
        # expected result not an exception
        return nullcontext(request.param)


def _extract_responses(
    fixture_data_dict: dict[str, dict[str, Any]],
    fixture_key: Literal["psf_responses_indirect", "psf_respx_mock_indirect"],
) -> None:
    """
    Extract responses data into a single list for the mock.

    This list will be added to the fixture data dict for a fixture with either the name
    "psf_responses" or "psf_respx_mock", with indirect=True. The fixture will only be
    exposed if the --psf-load-responses or --psf-load-respx flags are used. The name in
    the fixture data dict will be either "psf_responses_indirect" or
    "psf_respx_mock_indirect", which will then be processed later as an indirect
    fixture.

    :param fixture_data_dict: dict containing all parameterization data
    :type fixture_data_dict: dict[str, dict[str, Any]]
    :param fixture_key: name of the fixture key that will be added
    :type fixture_key: value must be "psf_responses_indirect" or "psf_respx_mock_indirect"
    """
    # for each scenario
    #   for each fixture
    #       check if fixture name ends with _responses or _response
    #           remove it from the fixture_data_dict
    #           add it to a list for the fixture for Responses or Respx
    for one_scenario in fixture_data_dict.values():
        # Note: have to do this in two stages as the dict keys
        # will be changing when we pop values off the dict. Trying to
        # iterate over the dict keys directly or using filter() will
        # result in an exception.
        responses_fixture_names = [
            one_fixture_name
            for one_fixture_name in one_scenario.keys()
            if one_fixture_name.endswith("_response") or one_fixture_name.endswith("_responses")
        ]
        psf_responses_data = []
        for one_fixture_name in responses_fixture_names:
            current_fixture_data = one_scenario.pop(one_fixture_name)
            # TODO: once Python 3.9 is EOL, change this to the cleaner structural
            #  pattern matching form.
            # It's entirely possible that the contents of either the list
            # or the dict are not usable, but that will be caught when the
            # mocks are constructed.
            if isinstance(current_fixture_data, list):
                psf_responses_data.extend(current_fixture_data)
            elif isinstance(current_fixture_data, dict):
                psf_responses_data.append(current_fixture_data)
            elif current_fixture_data is None:
                pass
            else:
                raise RuntimeError(f"Pytest-Scenario-Files: {one_fixture_name} is not a list or dict.")
        # It's possible to have a scenario where there are no responses, such
        # as a case where a fixture is auto-used but the particular scenario
        # doesn't actually make any HTTP calls so there's no need to mack anything
        # so we need to put in a list even if the length is zero.
        one_scenario[fixture_key] = psf_responses_data

    # at the end of this the fixture data dict has had all of the "_responses"
    # entries popped out of it and each scenario that has a "psf_responses_indirect" or
    # a "psf_respx_mock_indirect" fixture, depending on the fixture_key parameter.
    return


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Pytest hook function that does the parameterization.

    This is where the heavy lifting is done. The process is:

    1. Walk the directory tree looking for files that match the name of the test.
    2. Load test data from the files.
    3. Extract fixture names and check for consistency.
    4. (Optional) Gather data from all fixtures with the suffixes ``_response``
       or ``_responses`` into a single fixture for use with the Responses or
       Respx integrations.
    5. Get list of indirect fixtures and remove the suffix ``_indirect`` from
       indirect fixture names.
    6. Reformat the data into lists for the parameterization call.
    7. Make the function call.

    :param metafunc: Pytest fixture used to create the parameterization
    """
    # load up files in same or lower dirs that start with the same
    # name as the test function prefixed by data_
    # E.g.,
    # parameterize against list of names if match
    test_name = metafunc.definition.name.removeprefix("test_")
    test_file_dir = str(metafunc.definition.path.parent)

    fixture_raw_data_dict = _locate_and_load_test_data(test_name, test_file_dir)

    if len(fixture_raw_data_dict) > 0:
        # do processing only if the search found cases

        # if either the psf-load-responses or psf-load-respx flags is set, go through
        # the raw data dict to find any fixtures that end with _response or _responses.
        # If any are found, remove them and set up psf_responses_indirect or
        # psf_respx_mock_indirect as an indirect fixture.
        # TODO: when Python 3.9 is EOL, convert this to the cleaner structural pattern
        #  matching form.
        if _psf_configs.psf_load_responses:
            _extract_responses(fixture_raw_data_dict, "psf_responses_indirect")
        elif _psf_configs.psf_load_respx:
            _extract_responses(fixture_raw_data_dict, "psf_respx_mock_indirect")

        # get the list of fixture names sorted alphabetically
        # will raise an exception if the fixture names are inconsistent
        fixture_names = _extract_fixture_names(fixture_raw_data_dict)

        # pull out indirect fixtures and remove suffix from fixture names
        # The returned value for indirect_fixture_names could be False
        # if there are no indirect fixtures. (This comes from Metafunc.parameterize,
        # which expects a list of indirect fixtures or False. Why not an empty
        # list? I dunno?)
        fixture_names, indirect_fixture_names = _extract_indirect_fixtures(fixture_raw_data_dict, fixture_names)

        # reformat the case ids and fixture data into list and list of
        # lists respectively
        case_ids, fixture_data_list = _extract_fixture_data(fixture_raw_data_dict)

        # do the parameterization
        metafunc.parametrize(
            fixture_names, fixture_data_list, ids=case_ids, indirect=indirect_fixture_names, scope="function"
        )
