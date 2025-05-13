import responses


def test_responses_fixture_data_not_dict_or_list_tester(psf_responses, psf_expected_result):
    with psf_expected_result as expected_result:
        req_result = responses.get("https://www.example.com/")
        req_result.raise_for_status()
        assert req_result.body == expected_result
