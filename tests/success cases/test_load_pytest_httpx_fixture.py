"""Test indirect fixture loading"""

import pytest

# This isn't quite right; should be checking that the pytest-httpx plugin is
# loaded, not just that we can import it.
responses = pytest.importorskip("pytest_httpx")


def test_load_pytest_httpx_fixture_single(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_pytest_httpx_fixture_single_tester.py")
    test_file_path.rename("test_load_pytest_httpx_fixture_single_tester.py")

    # create the data file
    pytester.copy_example("data_load_pytest_httpx_fixture_single_tester_1.yaml")

    result = pytester.runpytest("-v", "--psf-load-httpx")

    result.assert_outcomes(passed=2)


def test_load_pytest_httpx_fixture_multiple(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_pytest_httpx_fixture_multiple_tester.py")
    test_file_path.rename("test_load_pytest_httpx_fixture_multiple_tester.py")

    # create the data file
    pytester.copy_example("data_load_pytest_httpx_fixture_multiple_tester_1.yaml")

    result = pytester.runpytest("-v", "--psf-load-httpx")

    result.assert_outcomes(passed=1)


def test_load_pytest_httpx_fixture_partial(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_pytest_httpx_fixture_partial_tester.py")
    test_file_path.rename("test_load_pytest_httpx_fixture_partial_tester.py")

    # create the data file
    pytester.copy_example("data_load_pytest_httpx_fixture_partial_tester_1.yaml")

    result = pytester.runpytest("-v", "--psf-load-httpx", "--psf-fire-all-responses")

    result.assert_outcomes(passed=1, errors=1)
