def test_load_by_reference_cli_additional_data_root_option(pytester):
    """The --psf-additional-data-root option is searched before the default search.

    With two directories that would otherwise both match the referenced filename (and
    therefore collide if searched together, e.g. from a whole-cwd walk), passing
    --psf-additional-data-root pointed at one of them resolves the reference there
    first, avoiding the collision and picking up that directory's data.

    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    real_dir = test_file_path.parent / "real_test_dir"
    real_dir.mkdir()
    test_file_path.rename("real_test_dir/test_load_by_reference_tester.py")

    data_file1_path = pytester.copy_example("data_load_by_reference_tester.yaml")
    data_file1_path.rename("real_test_dir/data_load_by_reference_tester.yaml")

    # the file referenced by data_load_by_reference_tester.yaml lives only under
    # additional_root, not next to the test/referencing file
    additional_root = pytester.path / "additional_root"
    additional_root.mkdir()
    (additional_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 88}}',
    )

    # an unrelated directory that also has a same-named file with different (bad) data -
    # would collide with the file above if both were searched together
    other_root = pytester.path / "other_root"
    other_root.mkdir()
    (other_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 999}}',
    )

    result = pytester.runpytest(
        "-k", "test_load_by_reference_tester", "-v", f"--psf-additional-data-root={additional_root}"
    )

    result.assert_outcomes(passed=2)


def test_load_by_reference_per_file_additional_data_root_variable(pytester):
    """A psf_additional_data_root list variable in the test file is searched first.

    Verifies that this per-test-file list takes effect even when a same-named colliding
    data file exists elsewhere under cwd that a plain (unscoped) search would otherwise
    trip over.

    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    real_dir = test_file_path.parent / "real_test_dir"
    real_dir.mkdir()
    test_file_path.rename("real_test_dir/test_load_by_reference_tester.py")

    data_file1_path = pytester.copy_example("data_load_by_reference_tester.yaml")
    data_file1_path.rename("real_test_dir/data_load_by_reference_tester.yaml")

    additional_root = pytester.path / "additional_root"
    additional_root.mkdir()
    (additional_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 88}}',
    )

    other_root = pytester.path / "other_root"
    other_root.mkdir()
    (other_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 999}}',
    )

    test_module_path = real_dir / "test_load_by_reference_tester.py"
    test_module_path.write_text(
        f"psf_additional_data_root = [{str(additional_root)!r}]\n\n" + test_module_path.read_text()
    )

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v")

    result.assert_outcomes(passed=2)


def test_load_by_reference_cli_roots_searched_before_per_file_roots(pytester):
    """CLI --psf-additional-data-root roots are tried before the test-file list.

    Both a CLI root and a test-file-level root are configured, each holding different
    data for the same reference. Only the CLI root's value should be used, since it is
    searched first.

    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    real_dir = test_file_path.parent / "real_test_dir"
    real_dir.mkdir()
    test_file_path.rename("real_test_dir/test_load_by_reference_tester.py")

    data_file1_path = pytester.copy_example("data_load_by_reference_tester.yaml")
    data_file1_path.rename("real_test_dir/data_load_by_reference_tester.yaml")

    cli_root = pytester.path / "cli_root"
    cli_root.mkdir()
    (cli_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 88}}',
    )

    in_file_root = pytester.path / "in_file_root"
    in_file_root.mkdir()
    (in_file_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 999}}',
    )

    test_module_path = real_dir / "test_load_by_reference_tester.py"
    test_module_path.write_text(
        f"psf_additional_data_root = [{str(in_file_root)!r}]\n\n" + test_module_path.read_text()
    )

    result = pytester.runpytest(
        "-k", "test_load_by_reference_tester", "-v", f"--psf-additional-data-root={cli_root}"
    )

    result.assert_outcomes(passed=2)


def test_load_by_reference_additional_root_miss_falls_back_to_default(pytester):
    """A miss in an additional root falls through to the default search, without error.

    This is the core point of psf_additional_data_root being additive rather than
    exclusive: trying an alternate root that doesn't happen to have the data must not
    prevent the reference from resolving via the referencing file's own directory.

    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    test_file_path.rename("test_load_by_reference_tester.py")

    pytester.copy_example("data_load_by_reference_tester.yaml")
    pytester.copy_example("data_merge_multi_fixtures_tester_2.json")

    # an additional root that exists but doesn't have the referenced data - should be
    # skipped over, falling back to the default search, rather than causing a failure
    empty_additional_root = pytester.path / "empty_additional_root"
    empty_additional_root.mkdir()

    result = pytester.runpytest(
        "-k", "test_load_by_reference_tester", "-v", f"--psf-additional-data-root={empty_additional_root}"
    )

    result.assert_outcomes(passed=2)
