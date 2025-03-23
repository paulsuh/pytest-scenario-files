"""See if the conflicting options logic works."""

import pytest


def test_conflicting_options(pytester):
    run_result: pytest.RunResult = pytester.runpytest("--psf-load-responses", "--psf-load-respx")

    assert run_result.ret == 4
    run_result.stderr.fnmatch_lines(
        ["ERROR: The --psf-load-resposes and --psf-load-respx options are mutually exclusive."]
    )
