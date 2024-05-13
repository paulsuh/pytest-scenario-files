def test_data_file_not_dict(pytester):
    test_file_path = pytester.copy_example("example_test_data_file_not_dict_tester.py")
    test_file_path.rename("test_data_file_not_dict_tester.py")

    # create the data files
    pytester.copy_example("data_data_file_not_dict_tester.yaml")

    result = pytester.runpytest("-k", "test_data_file_not_dict_tester", "-v")

    result.assert_outcomes(errors=1)
