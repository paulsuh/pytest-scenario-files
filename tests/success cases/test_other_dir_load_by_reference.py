def test_other_dir_load_by_reference(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    subdir_path = test_file_path.parent / "subdir1"
    subdir_path.mkdir()
    test_file_path.rename("subdir1/test_load_by_reference_tester.py")

    # create the data files
    data_file1_path = pytester.copy_example("data_load_by_reference_tester.yaml")
    data_file1_path.rename("subdir1/data_load_by_reference_tester.yaml")

    data_file2_path = pytester.copy_example("data_merge_multi_fixtures_tester_2.json")
    subdir2_path = data_file2_path.parent / "subdir2"
    subdir2_path.mkdir()
    data_file2_path.rename("subdir2/data_merge_multi_fixtures_tester_2.json")

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v")

    result.assert_outcomes(passed=2)
