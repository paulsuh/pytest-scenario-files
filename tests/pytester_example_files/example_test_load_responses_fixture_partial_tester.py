import pytest
import requests


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_load_responses_fixture_partial_tester(psf_responses, expected_result):
    for one_test in expected_result:
        req_result = requests.get(one_test["url"])
        assert req_result.text == one_test["text"]
