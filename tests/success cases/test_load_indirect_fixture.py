"""Test indirect fixture loading
"""


def test_load_indirect_fixture(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_indirect_fixture_tester.py")
    test_file_path.rename("test_load_indirect_fixture_tester.py")

    # create the data file
    pytester.copy_example("data_load_indirect_fixture_tester_1.yaml")

    result = pytester.runpytest("-k", "test_load_indirect_fixture_tester", "-v")

    result.assert_outcomes(passed=2)
