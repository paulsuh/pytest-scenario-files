def test_load_one_tester(paramfiledata):
    assert paramfiledata["input_data"] == paramfiledata["expected_result"]
