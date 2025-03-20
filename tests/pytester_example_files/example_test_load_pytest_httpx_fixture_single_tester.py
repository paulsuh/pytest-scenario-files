import httpx
import pytest


@pytest.mark.skipif('not config.getoption("psf-load-httpx", False)')
def test_load_pytest_httpx_fixture_single_tester(psf_httpx_mock, expected_result):
    with httpx.Client() as client:
        req_result = client.get("https://www.example.com/")
        assert req_result.text == expected_result
