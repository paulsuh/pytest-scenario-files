"""Test indirect fixture loading"""


def test_load_responses_fixture_single(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_responses_fixture_single_tester.py")
    test_file_path.rename("test_load_responses_fixture_single_tester.py")

    # create the data file
    pytester.copy_example("data_load_responses_fixture_single_tester_1.yaml")

    result = pytester.runpytest("-k", "test_load_responses_fixture_single_tester", "-v", "--psf-load-responses")

    result.assert_outcomes(passed=2)


def test_load_responses_fixture_multiple(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_responses_fixture_multiple_tester.py")
    test_file_path.rename("test_load_responses_fixture_multiple_tester.py")

    # create the data file
    pytester.copy_example("data_load_responses_fixture_multiple_tester_1.yaml")

    result = pytester.runpytest("-v", "--psf-load-responses")

    result.assert_outcomes(passed=1)
