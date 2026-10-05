def test_load_by_reference_ignores_stray_duplicate(pytester):
    """Regression test for a reference resolving via a stray duplicate elsewhere in cwd.

    Reproduces the bug where _load_referenced_data() searched from os.getcwd() downward,
    so any duplicate copy of a referenced data file's name anywhere under the current
    working directory (e.g. left behind in a stray git worktree) would collide with the
    real one during merging and raise BadTestCaseDataException. The reference should
    resolve using the referencing file's own directory first, so a stray duplicate
    elsewhere under cwd (outside of the referencing file's own subtree) must not affect
    the result.

    """
    # create the test code file and real data files together, in their own
    # subdirectory, so that a search rooted there won't also find the stray
    # duplicate created below
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    real_dir = test_file_path.parent / "real_test_dir"
    real_dir.mkdir()
    test_file_path.rename("real_test_dir/test_load_by_reference_tester.py")

    data_file1_path = pytester.copy_example("data_load_by_reference_tester.yaml")
    data_file1_path.rename("real_test_dir/data_load_by_reference_tester.yaml")

    data_file2_path = pytester.copy_example("data_merge_multi_fixtures_tester_2.json")
    data_file2_path.rename("real_test_dir/data_merge_multi_fixtures_tester_2.json")

    # simulate a stray duplicate of the referenced data file elsewhere under cwd,
    # in a sibling directory outside of the referencing file's own subtree - e.g.
    # left behind by an old worktree - with data that would collide if it were ever
    # merged with the real file's data
    stray_dir = pytester.path / "stray_worktree" / "some" / "nested" / "dir"
    stray_dir.mkdir(parents=True)
    (stray_dir / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 999}}',
    )

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v")

    result.assert_outcomes(passed=2)
