import pytest
import requests


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_native_responses_load_tester(psf_responses, psf_expected_result, target_url):
    with psf_expected_result as expected_result:
        req_result = requests.get(target_url)
        req_result.raise_for_status()
        assert req_result.text == expected_result
