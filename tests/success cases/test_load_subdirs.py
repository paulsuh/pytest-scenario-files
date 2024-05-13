def test_load_subdirs(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_subdirs_tester.py")
    test_file_path.rename("test_load_subdirs_tester.py")

    # create the data files
    pytester.copy_example("data_load_subdirs_tester_1.yaml")

    datafile2_path = pytester.copy_example("data_load_subdirs_tester_2.json")
    subdir_path = datafile2_path.parent / "subdir"
    subdir_path.mkdir()
    datafile2_path.rename(subdir_path / datafile2_path.name)

    result = pytester.runpytest("-k", "test_load_subdirs_tester", "-v")

    result.assert_outcomes(passed=4)
