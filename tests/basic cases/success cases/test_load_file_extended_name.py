"""A test that accidentally loads data intended for another test.

This shows how a test naming conflict can cause problems.

In the first unit test there are two files:

   data_load_one_tester_1.yaml
   data_load_one_file_tester.json

The second data file contains two scenarios and is intended for
test_load_one_file() but because the data file name also matches
against the shorter test_load_one(), both data files get loaded.
On top of that, both data files contain a test id "test_one", so
one of those conflicts with the other and results in an error.

In the second unit test there are also two files:

   data_load_one_tester_1.json
   data_load_one_file_tester.json

However, the test case id's do not conflict and instead the
sets of test data are merged normally, resulting in two test
cases being run instead of just one.
"""


def test_load_file_extended_name_conflict(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_one_tester.py")
    test_file_path.rename("test_load_one_tester.py")

    # create the data file
    pytester.copy_example("data_load_one_tester_1.yaml")
    pytester.copy_example("data_load_one_file_tester.json")

    result = pytester.runpytest("-k", "test_load_one_tester", "-v")

    result.assert_outcomes(errors=1)


def test_load_file_extended_name_no_conflict(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_one_tester.py")
    test_file_path.rename("test_load_one_tester.py")

    # create the data file
    pytester.copy_example("data_load_one_tester_1.json")
    pytester.copy_example("data_load_one_file_tester.json")

    result = pytester.runpytest("-k", "test_load_one_tester", "-v")

    result.assert_outcomes(passed=2)
