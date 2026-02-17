"""The second most basic test.

Load one test case from one file. If this doesn't work then nothing
more advanced is likely to work either.
"""


def test_load_one_file(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_one_file_tester.py")
    test_file_path.rename("test_load_one_file_tester.py")

    # create the data file
    pytester.copy_example("data_load_one_file_tester.json")

    result = pytester.runpytest("-k", "test_load_one_file_tester", "-v")

    result.assert_outcomes(passed=1)
