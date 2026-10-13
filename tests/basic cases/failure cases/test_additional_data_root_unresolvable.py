def test_load_by_reference_additional_root_collision_still_raises(pytester):
    """A reference matching twice within a single additional root is a collision.

    psf_additional_data_root is additive, not exclusive, but a collision *within* one
    of its roots (two files there matching the same scenario) is still an error - the
    same guarantee the default search provides.
    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    test_file_path.rename("test_load_by_reference_tester.py")

    pytester.copy_example("data_load_by_reference_tester.yaml")

    additional_root = pytester.path / "additional_root"
    sub_dir_1 = additional_root / "sub_dir_1"
    sub_dir_2 = additional_root / "sub_dir_2"
    sub_dir_1.mkdir(parents=True)
    sub_dir_2.mkdir(parents=True)
    (sub_dir_1 / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 88}}',
    )
    (sub_dir_2 / "data_merge_multi_fixtures_tester_2.json").write_text(
        '{"test_two": {"input_data_2": 999}}',
    )

    result = pytester.runpytest(
        "-k", "test_load_by_reference_tester", "-v", f"--psf-additional-data-root={additional_root}"
    )

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*BadTestCaseDataException*already loaded*"])


def test_load_by_reference_unresolvable_names_every_root_searched(pytester):
    """A reference not found anywhere raises, naming every root that was searched.

    With an additional root configured (that doesn't have the data), plus the default
    search (referencing file's directory, then cwd) also missing it, resolution must
    raise naming all of the roots that were tried, not just the default ones.
    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    real_dir = test_file_path.parent / "real_test_dir"
    real_dir.mkdir()
    test_file_path.rename("real_test_dir/test_load_by_reference_tester.py")

    data_file1_path = pytester.copy_example("data_load_by_reference_tester.yaml")
    data_file1_path.rename("real_test_dir/data_load_by_reference_tester.yaml")

    additional_root = pytester.path / "additional_root"
    additional_root.mkdir()

    # Note: the referenced data_merge_multi_fixtures_tester_2.json is never created
    # anywhere under the additional root, the referencing file's directory, or cwd.

    result = pytester.runpytest(
        "-k", "test_load_by_reference_tester", "-v", f"--psf-additional-data-root={additional_root}"
    )

    result.assert_outcomes(errors=1)
    output = str(result.stdout)
    assert "BadTestCaseDataException" in output
    assert str(additional_root) in output
    assert str(real_dir) in output
    assert str(pytester.path) in output


def test_load_by_reference_scenario_found_fixture_missing(pytester):
    """A resolved reference missing the requested fixture raises clearly.

    The referenced data file has the requested scenario, but not the requested
    fixture within it - this must be distinguished from a missing scenario/file.
    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    test_file_path.rename("test_load_by_reference_tester.py")

    pytester.copy_example("data_load_by_reference_tester.yaml")

    pytester.makefile(
        ".json",
        data_merge_multi_fixtures_tester_2="""\
{
  "test_one": {"input_data_2": "meep"},
  "test_two": {"some_other_fixture": 88}
}
""",
    )

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v")

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*BadTestCaseDataException*no fixture*input_data_2*"])
