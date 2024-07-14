# ruff: noqa: D103
# get_oauth_token.py
from requests import get, post


def _retrieve_secret(secret_id: str, lockbox_id: str = "54D7DB9B-DF43-4657-ABD9-F359E5F3DFA5") -> str:
    result = get(f"http://127.0.0.1:8200/v1/{lockbox_id}/{secret_id}")
    result.raise_for_status()
    return result.json()["data"][secret_id]


def get_token_service_A() -> str:
    result = post(
        "https://authserver.source-a.com/oauth2/token",
        json={
            "client_id": "clientIdA",
            "client_secret": _retrieve_secret("clientIdA"),
            "grant_type": "client_credentials",
        },
    )
    result.raise_for_status()
    return result.json()["access_token"]


def get_token_service_B() -> str:
    result = post(
        "https://authserver.source-b.com/oauth2/token",
        json={
            "client_id": "clientIdB",
            "client_secret": _retrieve_secret("clientIdB"),
            "grant_type": "client_credentials",
        },
    )
    result.raise_for_status()
    return result.json()["access_token"]
