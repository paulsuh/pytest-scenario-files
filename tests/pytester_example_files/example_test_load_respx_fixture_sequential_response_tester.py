from typing import Any

import httpx
import pytest
import respx


@pytest.mark.skipif('not config.getoption("psf-load-respx", False)')
def test_load_respx_fixture_sequential_response_tester(
    psf_respx_mock: respx.MockRouter, psf_expected_result: Any, expected_response_1: Any
) -> None:
    with psf_expected_result as expected_result:
        with httpx.Client() as client:
            req_result = client.get("https://www.example.com/")
            req_result.raise_for_status()
            assert req_result.text == expected_response_1

            req_result = client.get("https://www.example.com/")
            req_result.raise_for_status()
            assert req_result.text == expected_result
