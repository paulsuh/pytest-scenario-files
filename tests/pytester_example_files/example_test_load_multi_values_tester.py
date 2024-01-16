def test_load_multi_values_tester(paramfiledata):
    assert paramfiledata["input_data"] == paramfiledata["expected_result"]
