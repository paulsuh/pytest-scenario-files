from json import dumps


def test_load_one_file(pytester):
    # create the test code file
    pytester.makepyfile(
        test_load_one_file_tester="""
        def test_load_one_file_tester(paramfiledata):
            assert paramfiledata['input_data'] == paramfiledata['expected_result']
        """
    )

    # create the data file
    pytester.makefile(".json", data_load_one_file_tester=dumps({"test_one": {"input_data": 17, "expected_result": 17}}))

    result = pytester.runpytest("-k", "test_load_one_file_tester", "--param-from-files")

    result.assert_outcomes(passed=1)
