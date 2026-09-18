def test_load_by_reference_cli_reference_root_option(pytester):
    """The --psf-reference-root option pins the search root for reference resolution.

    With two directories that would otherwise both match the referenced filename (and
    therefore collide if searched together, e.g. from a whole-cwd walk), passing
    --psf-reference-root scoped to one of them resolves the reference using only that
    directory, avoiding the collision and picking up that directory's data.

    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    real_dir = test_file_path.parent / "real_test_dir"
    real_dir.mkdir()
    test_file_path.rename("real_test_dir/test_load_by_reference_tester.py")

    data_file1_path = pytester.copy_example("data_load_by_reference_tester.yaml")
    data_file1_path.rename("real_test_dir/data_load_by_reference_tester.yaml")

    # the file referenced by data_load_by_reference_tester.yaml lives only under
    # configured_root, not next to the test/referencing file
    configured_root = pytester.path / "configured_root"
    configured_root.mkdir()
    (configured_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 88}}',
    )

    # an unrelated directory that also has a same-named file with different (bad) data -
    # would collide with the file above if both were searched together
    other_root = pytester.path / "other_root"
    other_root.mkdir()
    (other_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 999}}',
    )

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v", f"--psf-reference-root={configured_root}")

    result.assert_outcomes(passed=2)


def test_load_by_reference_per_file_reference_root_variable(pytester):
    """A psf_reference_root variable in the test file overrides the search root.

    Verifies that this per-test-file override takes effect even when a same-named
    colliding data file exists elsewhere under cwd that a plain (unscoped) search would
    otherwise trip over.

    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    real_dir = test_file_path.parent / "real_test_dir"
    real_dir.mkdir()
    test_file_path.rename("real_test_dir/test_load_by_reference_tester.py")

    data_file1_path = pytester.copy_example("data_load_by_reference_tester.yaml")
    data_file1_path.rename("real_test_dir/data_load_by_reference_tester.yaml")

    configured_root = pytester.path / "configured_root"
    configured_root.mkdir()
    (configured_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 88}}',
    )

    other_root = pytester.path / "other_root"
    other_root.mkdir()
    (other_root / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 999}}',
    )

    test_module_path = real_dir / "test_load_by_reference_tester.py"
    test_module_path.write_text(f"psf_reference_root = {str(configured_root)!r}\n\n" + test_module_path.read_text())

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v")

    result.assert_outcomes(passed=2)


def test_load_by_reference_cli_beats_per_file_reference_root(pytester):
    """The --psf-reference-root option takes priority over psf_reference_root.

    Both a CLI root and a test-file-level root are configured, each holding different
    data for the same reference. Only the CLI root's value should be used.

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
    test_module_path.write_text(f"psf_reference_root = {str(in_file_root)!r}\n\n" + test_module_path.read_text())

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v", f"--psf-reference-root={cli_root}")

    result.assert_outcomes(passed=2)
