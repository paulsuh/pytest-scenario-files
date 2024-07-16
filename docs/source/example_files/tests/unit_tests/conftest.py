# ruff: noqa: D103
# conftest.py
from pytest import fixture
from responses import RequestsMock, matchers


@fixture
def client_secret_responses(request):
    with RequestsMock() as rsps:
        rsps.assert_all_requests_are_fired = False
        for one_response in request.param:
            rsps.add(
                url=one_response["url"],
                method=one_response["method"],
                status=one_response["status"],
                json=one_response["json"],
            )

        yield rsps


@fixture
def auth_tokens_responses(request, client_secret_responses: RequestsMock):
    for one_response in request.param:
        client_secret_responses.add(
            url=one_response["url"],
            method=one_response["method"],
            status=one_response["status"],
            match=[matchers.json_params_matcher(one_response["json_params"])],
            json=one_response["json"],
        )
    return client_secret_responses


@fixture
def api_1_responses(request, auth_tokens_responses: RequestsMock):
    for one_response in request.param:
        auth_tokens_responses.add(
            url=one_response["url"],
            method=one_response["method"],
            status=one_response["status"],
            json=one_response["json"],
        )
    return auth_tokens_responses
