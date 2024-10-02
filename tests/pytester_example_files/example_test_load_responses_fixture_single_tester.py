import requests


def test_load_responses_fixture_single_tester(expected_result):
    req_result = requests.get("https://www.example.com/")
    assert req_result.text == expected_result
