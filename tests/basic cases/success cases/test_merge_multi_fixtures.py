"""Merge fixtures from multiple files

If the same test case is defined in two or more files, the fixtures will
be merged together as long as there is no conflict.
"""


def test_merge_multi_fixtures(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_merge_multi_fixtures_tester.py")
    test_file_path.rename("test_merge_multi_fixtures_tester.py")

    # create the data files
    pytester.copy_example("data_merge_multi_fixtures_tester_1.yaml")
    pytester.copy_example("data_merge_multi_fixtures_tester_2.json")
    pytester.copy_example("data_merge_multi_fixtures_tester_3.yaml")

    result = pytester.runpytest("-k", "test_merge_multi_fixtures_tester", "-v")

    result.assert_outcomes(passed=3)
