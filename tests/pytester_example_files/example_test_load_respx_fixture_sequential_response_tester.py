from typing import Any

import httpx
import pytest
import respx


@pytest.mark.skipif('not config.getoption("psf-load-respx", False)')
def test_load_respx_fixture_sequential_response_tester(
    psf_respx_mock: respx.MockRouter, psf_expected_result: Any, all_expected_texts: list
) -> None:
    with psf_expected_result as expected_result:  # noqa F841
        with httpx.Client() as client:
            for one_exp_response in all_expected_texts:
                req_result = client.get("https://www.example.com/")
                req_result.raise_for_status()
                assert req_result.text == one_exp_response
