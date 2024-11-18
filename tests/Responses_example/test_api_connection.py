import pytest
from api_connection import NetBrainConnection


@pytest.fixture
def netbrain_connection_obj() -> NetBrainConnection:
    return NetBrainConnection("username", "mock_password", "mock_tenant_name", "mock_domain_name")


def test_login_to_api(psf_responses, psf_expected_result, netbrain_connection_obj):
    with psf_expected_result as expected_result:
        netbrain_connection_obj.login_to_api()
        assert netbrain_connection_obj.nb_req_headers["token"] == expected_result


def test_get_tenant_id(psf_responses, psf_expected_result, netbrain_connection_obj):
    with psf_expected_result as expected_result:
        netbrain_connection_obj.get_tenant_id()
        assert netbrain_connection_obj.tenant_id == expected_result


def test_get_domain_id(psf_responses, psf_expected_result, netbrain_connection_obj):
    with psf_expected_result as expected_result:
        netbrain_connection_obj.get_domain_id()
        assert netbrain_connection_obj.domain_id == expected_result


def test_set_tenant_and_domain(psf_responses, psf_expected_result, netbrain_connection_obj):
    with psf_expected_result as expected_result:  # noqa F841
        netbrain_connection_obj.set_tenant_and_domain()
        # set_tenant_and_domain() doesn't change anything on the client side
        # so just check that there is no exception thrown.
