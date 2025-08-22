import pytest
import requests


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_native_responses_load_tester(psf_responses, psf_expected_result):
    with psf_expected_result as expected_result:
        req_result = requests.get("https://httpstat.us/202")
        assert req_result.text == expected_result
