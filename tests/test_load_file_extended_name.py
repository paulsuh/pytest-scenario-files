def test_load_file_extended_name(pytester):
    # NOTE: This shows how a test naming conflict can step on another test.
    # There are two files:
    #    data_load_one_tester_1.yaml
    #    data_load_one_file_tester.json
    #
    # The second contains two scenarios and is intended for a test_load_one_file()
    # but because the data file name matches against the shorter test_load_one()
    # as well the intended test both get loaded. On top of that, both data files
    # contain a test id "test_one", so one of those replaces the other.

    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_one_tester.py")
    test_file_path.rename("test_load_one_tester.py")

    # create the data file
    pytester.copy_example("data_load_one_tester_1.yaml")
    pytester.copy_example("data_load_one_file_tester.json")

    result = pytester.runpytest("-k", "test_load_one_tester", "--param-from-files", "-v")

    result.assert_outcomes(passed=2)
