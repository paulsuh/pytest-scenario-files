# ruff: noqa: D103
# test_apis.py
import src.apis as apis


def test_api_1(api_1_responses, api_1_expected_result):
    assert apis.call_api_1() == api_1_expected_result
