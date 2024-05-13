def test_separate_subdirs(pytester):
    # create the test code files
    test_file1_path = pytester.copy_example("example_test_load_one_file_tester.py")
    subdir1_path = test_file1_path.parent / "subdir1"
    subdir1_path.mkdir()
    test_file1_path.rename("subdir1/test_load_one_file_tester.py")

    test_file2_path = pytester.copy_example("example_test_load_one_tester.py")
    subdir2_path = test_file2_path.parent / "subdir2"
    subdir2_path.mkdir()
    test_file2_path.rename("subdir2/test_load_one_tester.py")

    # create the data files
    datafile1_path = pytester.copy_example("data_load_one_file_tester.json")
    datafile1_path.rename(datafile1_path.parent / "subdir1" / datafile1_path.name)
    datafile2_path = pytester.copy_example("data_load_one_tester_1.yaml")
    datafile2_path.rename(datafile2_path.parent / "subdir2" / datafile2_path.name)

    result1 = pytester.runpytest("-k", "test_load_one_file_tester", "-v", "-rA")
    result1.assert_outcomes(passed=1)

    result2 = pytester.runpytest("-k", "test_load_one_tester", "-v", "-rA")
    result2.assert_outcomes(passed=2)
