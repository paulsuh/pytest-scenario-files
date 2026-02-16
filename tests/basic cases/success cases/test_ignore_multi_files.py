"""Check that data files that don't match are ignored.

This will only load and run the test cases from the first file, since the other two
data files don't have a name that matches the test.
"""


def test_ignore_multi_files(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_ignore_multi_files_tester.py")
    test_file_path.rename("test_ignore_multi_files_tester.py")

    # create the data files
    datafile1_path = pytester.copy_example("data_load_multi_files_tester_1.yaml")
    datafile1_path.rename("data_ignore_multi_files_tester_1.yaml")
    pytester.copy_example("data_load_multi_files_tester_2.json")
    pytester.copy_example("data_load_multi_files_tester_3.yaml")

    result = pytester.runpytest("-k", "test_ignore_multi_files_tester", "-v")

    result.assert_outcomes(passed=2)
