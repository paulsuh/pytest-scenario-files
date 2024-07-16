# ruff: noqa: D103
# apis.py
from time import sleep

from requests import get

from .get_oauth_token import get_token_service_A, get_token_service_B


def call_api_1():
    auth_token = get_token_service_A()

    api_response = get("https://api1endpoint.example.com/rest/foo", headers={"Authorization": f"Bearer {auth_token}"})
    api_response.raise_for_status()
    return api_response.json()


def call_api_2():
    auth_token = get_token_service_A()

    api_init_response = get(
        "https://api2endpoint.example.org/rest/bar/initiate", headers={"Authorization": f"Bearer {auth_token}"}
    )
    api_init_response.raise_for_status()
    request_id = api_init_response.json()["requestId"]

    for i in range(10):
        api_retrieve_response = get(
            f"https://api2endpoint.example.org/rest/bar/{request_id}", headers={"Authorization": f"Bearer {auth_token}"}
        )
        api_retrieve_response.raise_for_status()
        if len(api_retrieve_response.text) > 0:
            return api_retrieve_response.json()
        sleep(1)

    raise RuntimeError("API2 timed out")


def call_api_3():
    auth_token = get_token_service_B()

    api_result = get("https://api3endpoint.example.net/rest/baz", headers={"Authorization": f"Bearer {auth_token}"})
    api_result.raise_for_status()
    return api_result.text
