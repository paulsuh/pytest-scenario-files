def test_load_by_reference(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    test_file_path.rename("test_load_by_reference_tester.py")

    # create the data files
    pytester.copy_example("data_load_by_reference_tester.yaml")
    pytester.copy_example("data_merge_multi_fixtures_tester_2.json")

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v")

    result.assert_outcomes(passed=2)
