import pytest

# skip these tests if the responses module is not present
responses = pytest.importorskip("responses")


def test_responses_fixture_data_not_dict_or_list(pytester):
    test_file_path = pytester.copy_example("example_test_responses_fixture_data_not_dict_or_list_tester.py")
    test_file_path.rename("test_responses_fixture_data_not_dict_or_list_tester.py")

    # create the data files
    pytester.copy_example("data_responses_fixture_data_not_dict_or_list_tester_1.yaml")

    result = pytester.runpytest(
        "-k", "test_responses_fixture_data_not_dict_or_list_tester", "--psf-load-responses", "-v"
    )

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines("E   RuntimeError: Pytest-Scenario-Files: example_responses is not a list or dict.")
