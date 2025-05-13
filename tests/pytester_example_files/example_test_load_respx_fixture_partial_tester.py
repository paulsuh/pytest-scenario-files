import httpx
import pytest


@pytest.mark.skipif('not config.getoption("psf-load-respx", False)')
def test_load_respx_fixture_partial_tester(psf_respx_mock, expected_result):
    with httpx.Client() as client:
        for one_test in expected_result:
            req_result = client.get(one_test["url"])
            assert req_result.text == one_test["text"]
