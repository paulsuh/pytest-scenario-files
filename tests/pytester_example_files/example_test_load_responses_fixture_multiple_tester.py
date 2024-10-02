import requests


def test_load_responses_fixture_multiple_tester(expected_result):
    for one_test in expected_result:
        req_result = requests.get(one_test["url"])
        assert req_result.text == one_test["text"]
