import pytest
from api_connection import NetBrainConnection

# skip these tests if the responses module is not present
responses = pytest.importorskip("responses")


@pytest.fixture
def netbrain_connection_obj() -> NetBrainConnection:
    return NetBrainConnection("username", "mock_password", "mock_tenant_name", "mock_domain_name")


@pytest.fixture
def url_response_override(
    request: pytest.FixtureRequest,
    psf_responses: responses.RequestsMock,  # type:ignore[name-defined]
) -> responses.RequestsMock:  # type:ignore[name-defined]
    # NOTE: mypy gets cranky since it doesn't understand pytest.importorskip(), so
    # ignore type errors on responses.RequestsMock
    if hasattr(request, "param") and isinstance(request.param, dict):
        psf_responses.upsert(**request.param)
    return psf_responses


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_connect_to_api(url_response_override, psf_expected_result, netbrain_connection_obj):
    with psf_expected_result as expected_result:
        netbrain_connection_obj.connect_to_api()
        assert netbrain_connection_obj.nb_req_headers["token"] == expected_result


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_login_to_api(url_response_override, psf_expected_result, netbrain_connection_obj):
    with psf_expected_result as expected_result:
        netbrain_connection_obj.login_to_api()
        assert netbrain_connection_obj.nb_req_headers["token"] == expected_result


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_get_tenant_id(url_response_override, psf_expected_result, netbrain_connection_obj):
    with psf_expected_result as expected_result:
        netbrain_connection_obj.get_tenant_id()
        assert netbrain_connection_obj.tenant_id == expected_result


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_get_domain_id(url_response_override, psf_expected_result, netbrain_connection_obj):
    with psf_expected_result as expected_result:
        netbrain_connection_obj.get_domain_id()
        assert netbrain_connection_obj.domain_id == expected_result


@pytest.mark.skipif('not config.getoption("psf-load-responses", False)')
def test_set_tenant_and_domain(url_response_override, psf_expected_result, netbrain_connection_obj):
    with psf_expected_result as expected_result:  # noqa F841
        netbrain_connection_obj.set_tenant_and_domain()
        # set_tenant_and_domain() doesn't change anything on the client side
        # so just check that there is no exception thrown.
