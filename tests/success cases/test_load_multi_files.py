"""Load multiple test cases from multiple files.

The files can be both JSON and YAML format and may contain more than one
test case each.
"""


def test_load_multi_files(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_multi_files_tester.py")
    test_file_path.rename("test_load_multi_files_tester.py")

    # create the data files
    pytester.copy_example("data_load_multi_files_tester_1.yaml")
    pytester.copy_example("data_load_multi_files_tester_2.json")
    pytester.copy_example("data_load_multi_files_tester_3.yaml")

    result = pytester.runpytest("-k", "test_load_multi_files_tester", "-v")

    result.assert_outcomes(passed=5)
