import httpx
import pytest


@pytest.mark.skipif('not config.getoption("psf-load-respx", False)')
def test_respx_assert_all_mocked_flag_tester(psf_respx_mock, psf_expected_result, target_urls):
    with psf_expected_result as expected_result:
        with httpx.Client() as client:
            for one_url in target_urls:
                req_result = client.get(one_url)
                req_result.raise_for_status()
                assert req_result.text == expected_result
