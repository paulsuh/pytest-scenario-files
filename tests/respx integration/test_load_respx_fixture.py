"""Test indirect fixture loading"""

import pytest

respx = pytest.importorskip("respx")


def test_load_respx_fixture_single(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_respx_fixture_single_tester.py")
    test_file_path.rename("test_load_respx_fixture_single_tester.py")

    # create the data file
    pytester.copy_example("data_load_respx_fixture_single_tester_1.yaml")

    result = pytester.runpytest("-v", "--psf-load-respx")

    result.assert_outcomes(passed=2)


def test_load_respx_fixture_multiple(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_respx_fixture_multiple_tester.py")
    test_file_path.rename("test_load_respx_fixture_multiple_tester.py")

    # create the data file
    pytester.copy_example("data_load_respx_fixture_multiple_tester_1.yaml")

    result = pytester.runpytest("-v", "--psf-load-respx")

    result.assert_outcomes(passed=1)


def test_load_respx_fixture_partial(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_respx_fixture_partial_tester.py")
    test_file_path.rename("test_load_respx_fixture_partial_tester.py")

    # create the data file
    pytester.copy_example("data_load_respx_fixture_partial_tester_1.yaml")

    result = pytester.runpytest("-v", "--psf-load-respx", "--psf-assert-all-called")

    result.assert_outcomes(passed=1, errors=1)


def test_load_respx_fixture_update_response(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_respx_fixture_update_response_tester.py")
    test_file_path.rename("test_load_respx_fixture_update_response_tester.py")

    # create the data file
    pytester.copy_example("data_load_respx_fixture_update_response_tester_1.yaml")

    result = pytester.runpytest("-v", "-rA", "--psf-load-respx")

    result.assert_outcomes(passed=2)


def test_load_respx_fixture_sequential_response(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_respx_fixture_sequential_response_tester.py")
    test_file_path.rename("test_load_respx_fixture_sequential_response_tester.py")

    # create the data file
    pytester.copy_example("data_load_respx_fixture_sequential_response_tester_1.yaml")

    result = pytester.runpytest("-v", "-rA", "--psf-load-respx")

    result.assert_outcomes(passed=2, failed=1)


def test_respx_assert_all_mocked_flag(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_respx_assert_all_mocked_flag_tester.py")
    test_file_path.rename("test_respx_assert_all_mocked_flag_tester.py")

    # create the data file
    pytester.copy_example("data_respx_assert_all_mocked_flag_tester_1.yaml")

    result = pytester.runpytest("-v", "-rA", "--psf-load-respx", "--psf-assert-all-mocked")

    result.assert_outcomes(passed=2, failed=1)


def test_respx_assert_all_called_flag(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_respx_assert_all_called_flag_tester.py")
    test_file_path.rename("test_respx_assert_all_called_flag_tester.py")

    # create the data file
    pytester.copy_example("data_respx_assert_all_called_flag_tester_1.yaml")

    result = pytester.runpytest("-v", "-rA", "--psf-load-respx", "--psf-assert-all-called")

    # Note: test_three succeeds initially, but then Respx raises an exception
    # since not all of the mocks are called.
    # =========================== short test summary info ============================
    # PASSED test_respx_assert_all_called_flag_tester.py::test_respx_assert_all_called_flag_tester[test_one]
    # PASSED test_respx_assert_all_called_flag_tester.py::test_respx_assert_all_called_flag_tester[test_two]
    # PASSED test_respx_assert_all_called_flag_tester.py::test_respx_assert_all_called_flag_tester[test_three]
    # ERROR test_respx_assert_all_called_flag_tester.py::test_respx_assert_all_called_flag_tester[test_three]
    # ========================== 3 passed, 1 error in 0.09s ==========================
    result.assert_outcomes(passed=3, errors=1)
