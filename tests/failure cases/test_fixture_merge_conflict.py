def test_fixture_merge_conflict(pytester):
    test_file_path = pytester.copy_example("example_test_fixture_merge_conflict_tester.py")
    test_file_path.rename("test_fixture_merge_conflict_tester.py")

    # create the data files
    pytester.copy_example("data_fixture_merge_conflict_tester_1.yaml")
    pytester.copy_example("data_fixture_merge_conflict_tester_2.yaml")

    result = pytester.runpytest("-k", "test_fixture_merge_conflict_tester", "-v")

    result.assert_outcomes(errors=1)
