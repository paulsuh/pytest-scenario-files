def test_help_message(pytester):
    result = pytester.runpytest(
        "--help",
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(
        [
            "Parameterize from files plug-in:",
            "*--param-from-files*Parameterize unit tests with values loaded from files.",
        ]
    )
