import httpx
import pytest


@pytest.mark.skipif('not config.getoption("psf-load-respx", False)')
def test_load_respx_fixture_single_tester(psf_respx_mock, psf_expected_result):
    with psf_expected_result as expected_result:
        with httpx.Client() as client:
            req_result = client.get("https://www.example.com/")
            req_result.raise_for_status()
            assert req_result.text == expected_result
