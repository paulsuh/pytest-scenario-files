from typing import Any

import httpx
import pytest
import respx


@pytest.mark.skipif('not config.getoption("psf-load-respx", False)')
def test_load_respx_fixture_update_response_tester(
    psf_respx_mock: respx.MockRouter, psf_expected_result: Any, substitute_value: Any
) -> None:
    # update the response for https://www.example.com/
    if substitute_value is not None:
        psf_respx_mock.route(method="GET", url="https://www.example.com/").respond(
            status_code=200, text=substitute_value
        )
        psf_expected_result.enter_result = substitute_value

    # httpx.HTTPError
    with psf_expected_result as expected_result:
        with httpx.Client() as client:
            req_result = client.get("https://www.example.com/")
            req_result.raise_for_status()
            assert req_result.text == expected_result
