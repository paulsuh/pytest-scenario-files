def test_load_one_file_tester(paramfiledata):
    print(paramfiledata["input_data"])
    assert paramfiledata["input_data"] == paramfiledata["expected_result"]
