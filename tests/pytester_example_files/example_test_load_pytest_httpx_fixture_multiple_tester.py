import httpx
import pytest


@pytest.mark.skipif('not config.getoption("psf-load-httpx", False)')
def test_load_pytest_httpx_fixture_multiple_tester(psf_httpx_mock, expected_result):
    with httpx.Client() as client:
        for one_test in expected_result:
            req_result = client.get(one_test["url"])
            assert req_result.text == one_test["text"]
