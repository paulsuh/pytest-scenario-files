"""Load multiple test cases from one file.

This also tests loading from a YAML file as well.
"""


def test_psf_response_not_in_datafile(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_psf_response_not_in_datafile_tester.py")
    test_file_path.rename("test_psf_response_not_in_datafile_tester.py")

    # create the data file
    pytester.copy_example("data_psf_response_not_in_datafile_tester.yaml")

    result = pytester.runpytest("-k", "test_psf_response_not_in_datafile", "-v", "--psf-load-responses")

    result.assert_outcomes(passed=2)
