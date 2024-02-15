import pytest


@pytest.fixture
def indirect_fixture_test(request):
    return request.param * 5


def test_load_indirect_fixture_tester(indirect_fixture_test, expected_result):
    print(indirect_fixture_test)
    print(expected_result)
    assert indirect_fixture_test == expected_result
