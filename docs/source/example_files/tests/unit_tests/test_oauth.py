# ruff: noqa: D103
# test_oauth.py
import pytest
from requests import HTTPError

import src.get_oauth_token as get_oauth_token


def test_retrieve_secret(client_secret_responses, client_id, expected_secret):
    if expected_secret is None:
        with pytest.raises(HTTPError):
            get_oauth_token._retrieve_secret(client_id)
    else:
        assert get_oauth_token._retrieve_secret(client_id) == expected_secret


def test_get_oauth_token(auth_tokens_responses, client_id, expected_oauth_token):
    if client_id.endswith("A"):
        if expected_oauth_token is None:
            with pytest.raises(HTTPError):
                get_oauth_token.get_token_service_A()
        else:
            assert get_oauth_token.get_token_service_A() == expected_oauth_token
    else:
        if expected_oauth_token is None:
            with pytest.raises(HTTPError):
                assert get_oauth_token.get_token_service_B() == expected_oauth_token
        else:
            assert get_oauth_token.get_token_service_B() == expected_oauth_token
