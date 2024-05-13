def test_no_data_files_found(pytester):
    test_file_path = pytester.copy_example("example_test_no_data_files_found_tester.py")
    test_file_path.rename("test_no_data_files_found_tester.py")

    # no data files!

    result = pytester.runpytest("-k", "test_no_data_files_found_tester", "-v")

    result.assert_outcomes(errors=1)
