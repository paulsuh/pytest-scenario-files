# ruff: noqa: D103
# test_oauth.py
import src.get_oauth_token as get_oauth_token


def test_retrieve_secret(client_secret, client_id, expected_secret):
    assert get_oauth_token._retrieve_secret(client_id) == expected_secret


def test_get_oauth_token(auth_tokens, expected_oauth_token):
    if expected_oauth_token.endswith("A"):
        assert get_oauth_token.get_token_service_A() == expected_oauth_token
    else:
        assert get_oauth_token.get_token_service_B() == expected_oauth_token
