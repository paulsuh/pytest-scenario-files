import pytest
import requests


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_load_responses_fixture_empty_tester(psf_responses, psf_expected_result):
    with psf_expected_result as expected_result:
        req_result = requests.get("https://www.example.com/")
        assert req_result.text == expected_result
