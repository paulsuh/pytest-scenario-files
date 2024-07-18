# ruff: noqa: D103
# test_apis.py
import src.apis as apis


def test_api_1(api_responses, api_expected_result):
    api_result = apis.call_api_1()
    assert api_result["api_success"] == api_expected_result["api_success"]
    assert api_result["api_value"] == api_expected_result["api_value"]


def test_api_2_success(api_responses, api_expected_result):
    api_result = apis.call_api_2()
    assert api_result["api_success"] == api_expected_result["api_success"]
    assert api_result["api_value"] == api_expected_result["api_value"]
