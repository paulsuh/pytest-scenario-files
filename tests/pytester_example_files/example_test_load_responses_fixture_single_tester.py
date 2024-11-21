import pytest
import requests


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_load_responses_fixture_single_tester(psf_responses, expected_result):
    req_result = requests.get("https://www.example.com/")
    assert req_result.text == expected_result
