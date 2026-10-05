import pytest


@pytest.mark.parametrize("root_exists", [True, False], ids=["empty_dir", "nonexistent_dir"])
def test_load_by_reference_cli_root_exclusive(pytester, root_exists):
    """A configured --psf-reference-root is exclusive: no fallback on a miss.

    The referenced file sits right next to the referencing file, but
    --psf-reference-root points elsewhere. Resolution must fail rather than
    silently falling back to the referencing file's own directory - whether the
    configured root exists and is simply empty, or doesn't exist at all (os.walk()
    silently yields nothing for a missing directory, so both must raise the same
    way rather than the missing-directory case crashing differently).
    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    test_file_path.rename("test_load_by_reference_tester.py")

    pytester.copy_example("data_load_by_reference_tester.yaml")
    pytester.copy_example("data_merge_multi_fixtures_tester_2.json")

    configured_root = pytester.path / "configured_root"
    if root_exists:
        configured_root.mkdir()

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v", f"--psf-reference-root={configured_root}")

    result.assert_outcomes(errors=1)


def test_load_by_reference_per_file_root_exclusive(pytester):
    """A configured psf_reference_root variable is exclusive: no fallback on a miss.

    Same as the CLI-option case, but driven by the test-file-level variable rather
    than the command line.
    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    test_file_path.rename("test_load_by_reference_tester.py")

    pytester.copy_example("data_load_by_reference_tester.yaml")
    pytester.copy_example("data_merge_multi_fixtures_tester_2.json")

    empty_root = pytester.path / "empty_root"
    empty_root.mkdir()

    test_module_path = pytester.path / "test_load_by_reference_tester.py"
    test_module_path.write_text(f"psf_reference_root = {str(empty_root)!r}\n\n" + test_module_path.read_text())

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v")

    result.assert_outcomes(errors=1)


def test_load_by_reference_exclusive_root_error_names_root_searched(pytester):
    """An exclusive-root resolution failure names the exception and root searched.

    Dedicated test for the error *message contract* of the exclusive-root failure
    path (BadTestCaseDataException naming the configured root), kept separate from
    the tests above that only assert the failure occurs - so a future rewording of
    the message only needs to update this one test.
    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    test_file_path.rename("test_load_by_reference_tester.py")

    pytester.copy_example("data_load_by_reference_tester.yaml")
    pytester.copy_example("data_merge_multi_fixtures_tester_2.json")

    empty_root = pytester.path / "empty_root"
    empty_root.mkdir()

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v", f"--psf-reference-root={empty_root}")

    result.assert_outcomes(errors=1)
    result.stdout.fnmatch_lines(["*BadTestCaseDataException*", f"*{empty_root}*"])


def test_load_by_reference_unresolvable_no_root_configured(pytester):
    """A reference not found in the referencing directory or cwd raises clearly.

    With no root configured, the search tries the referencing file's own
    directory, falls back to cwd, and must raise (not KeyError) naming both roots
    it searched when neither has the referenced data.
    """
    test_file_path = pytester.copy_example("example_test_load_by_reference_tester.py")
    real_dir = test_file_path.parent / "real_test_dir"
    real_dir.mkdir()
    test_file_path.rename("real_test_dir/test_load_by_reference_tester.py")

    data_file1_path = pytester.copy_example("data_load_by_reference_tester.yaml")
    data_file1_path.rename("real_test_dir/data_load_by_reference_tester.yaml")

    # Note: the referenced data_merge_multi_fixtures_tester_2.json is never created
    # anywhere under the referencing file's directory or cwd.

    result = pytester.runpytest("-k", "test_load_by_reference_tester", "-v")

    result.assert_outcomes(errors=1)
    output = str(result.stdout)
    assert "BadTestCaseDataException" in output
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
