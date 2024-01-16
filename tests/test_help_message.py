def test_help_message(pytester):
    result = pytester.runpytest(
        "--help",
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "parameterize-from-files:",
            "*--param-from-files*Parameterize unit tests with values loaded from files.",
        ]
    )
