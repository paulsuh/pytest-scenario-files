def test_ignore_multi_files_tester(paramfiledata):
    assert paramfiledata["input_data"] == paramfiledata["expected_result"]
