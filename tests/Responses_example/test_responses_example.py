import pytest

# skip these tests if the responses module is not present
responses = pytest.importorskip("responses")


def test_api_connection_example(pytester):
    # create the test code file
    test_file_path = pytester.copy_example("../Responses_example/example_test_api_connection.py")
    test_file_path.rename("test_api_connection.py")

    # copy the data files and target code
    pytester.copy_example("../Responses_example/api_connection.py")
    pytester.copy_example("../Responses_example/common_test_data.yaml")
    pytester.copy_example("../Responses_example/data_connect_to_api.yaml")
    pytester.copy_example("../Responses_example/data_get_domain_id.yaml")
    pytester.copy_example("../Responses_example/data_get_tenant_id.yaml")
    pytester.copy_example("../Responses_example/data_login_to_api.yaml")
    pytester.copy_example("../Responses_example/data_set_tenant_and_domain.yaml")

    result = pytester.runpytest("-v", "--psf-load-responses")

    result.assert_outcomes(passed=15)
