"""Test indirect fixture loading"""

import pytest

# skip these tests if the responses module is not present
responses = pytest.importorskip("responses")


def test_load_native_responses_failure_bad_filename(pytester: pytest.Pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_native_responses_failure_tester.py")
    test_file_path.rename("test_native_responses_failure_tester.py")

    # create the data file and native Responses file
    pytester.copy_example("data_native_responses_failure_tester_bad_filename.yaml")

    result = pytester.runpytest("-v", "--psf-load-responses")

    result.assert_outcomes(errors=1)


def test_load_native_responses_failure_duplicate_files(pytester: pytest.Pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_native_responses_failure_tester.py")
    test_file_path.rename("test_native_responses_failure_tester.py")

    # create the data file and two copies of the native Responses file
    pytester.copy_example("data_native_responses_failure_tester_duplicate_files.yaml")

    # first copy goes into subdir
    datafile_path = pytester.copy_example("responses_replay_data.yaml")
    subdir_path = datafile_path.parent / "subdir"
    subdir_path.mkdir()
    datafile_path.rename(subdir_path / datafile_path.name)

    # second copy at top level
    pytester.copy_example("responses_replay_data.yaml")

    result = pytester.runpytest("-v", "--psf-load-responses")

    result.assert_outcomes(errors=1)
