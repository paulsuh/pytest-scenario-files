def test_fixture_mismatch(pytester):
    test_file_path = pytester.copy_example("example_test_fixture_mismatch_tester.py")
    test_file_path.rename("test_fixture_mismatch_tester.py")

    # create the data files
    pytester.copy_example("data_fixture_mismatch_tester_1.yaml")
    pytester.copy_example("data_fixture_mismatch_tester_2.yaml")

    result = pytester.runpytest("-k", "test_fixture_mismatch_tester", "-v")

    result.assert_outcomes(errors=1)
