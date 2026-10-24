"""Tests for expected_exception_name key in psf_expected_result_indirect.

Covers:
- New expected_exception_name key (builtin exceptions)
- New expected_exception_name key (module-level exceptions)
- Legacy expected_exception_type key still works
- Non-dict values still work (nullcontext path)
- expected_exception_name with match argument
"""

import textwrap


def test_expected_exception_name_builtin(pytester):
    """Test that expected_exception_name works with builtin exceptions."""
    pytester.makepyfile(
        test_value_error=textwrap.dedent("""
            def test_value_error(psf_expected_result):
                with psf_expected_result:
                    raise ValueError("expected failure")
        """)
    )
    pytester.makefile(
        ".yaml",
        data_value_error=textwrap.dedent("""
            test_value_error:
              psf_expected_result_indirect:
                expected_exception_name: ValueError
        """),
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1, warnings=0)


def test_expected_exception_name_module_level(pytester):
    """Test that expected_exception_name works with module-level exceptions."""
    pytester.makepyfile(
        test_http_error=textwrap.dedent("""
            import requests

            def test_http_error(psf_expected_result):
                with psf_expected_result:
                    raise requests.HTTPError("403")
        """)
    )
    pytester.makefile(
        ".yaml",
        data_http_error=textwrap.dedent("""
            test_http_error:
              psf_expected_result_indirect:
                expected_exception_name: requests.HTTPError
        """),
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1, warnings=0)


def test_expected_exception_type_legacy_still_works(pytester):
    """Test that legacy expected_exception_type key still works (with deprecation warning)."""
    pytester.makepyfile(
        test_legacy_type=textwrap.dedent("""
            def test_legacy_type(psf_expected_result):
                with psf_expected_result:
                    raise ValueError("legacy")
        """)
    )
    pytester.makefile(
        ".yaml",
        data_legacy_type=textwrap.dedent("""
            test_legacy_type:
              psf_expected_result_indirect:
                expected_exception_type: ValueError
        """),
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1, warnings=1)


def test_expected_exception_name_non_dict_value(pytester):
    """Test that non-dict values still work (nullcontext path)."""
    pytester.makepyfile(
        test_plain_value=textwrap.dedent("""
            def test_plain_value(psf_expected_result):
                with psf_expected_result as result:
                    assert result == 42
        """)
    )
    pytester.makefile(
        ".yaml",
        data_plain_value=textwrap.dedent("""
            test_plain_value:
              psf_expected_result_indirect: 42
        """),
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1, warnings=0)


def test_expected_exception_name_with_match(pytester):
    """Test that expected_exception_name works with match argument."""
    pytester.makepyfile(
        test_match=textwrap.dedent("""
            def test_match(psf_expected_result):
                with psf_expected_result:
                    raise ValueError("specific message")
        """)
    )
    pytester.makefile(
        ".yaml",
        data_match=textwrap.dedent("""
            test_match:
              psf_expected_result_indirect:
                expected_exception_name: ValueError
                match: "specific message"
        """),
    )
    result = pytester.runpytest("-v")
    result.assert_outcomes(passed=1, warnings=0)
