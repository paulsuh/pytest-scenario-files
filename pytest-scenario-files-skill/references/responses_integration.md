# Responses Integration

Load HTTP responses from data files into the
[Responses](https://github.com/getsentry/responses) package.

## Basic Usage

1. **Enable**: Run pytest with `--psf-load-responses`.
2. **Fixture**: Add `psf_responses` to your test function. It is a
   `RequestsMock` object with scenario data pre-loaded.
3. **Optional**: Use `--psf-fire-all-responses=true` to enable
   `assert_all_requests_are_fired`.

## Data Format

Define mocks in fixtures ending with `_response` or `_responses`.

### Single Response

```yaml
scenario_1:
  api_response:
    method: GET
    url: https://api.example.com/data
    status: 200
    json: {key: value}        # 'json' (auto-sets content-type) or 'body' (text)
    headers: {X-Test: foo}
```

### Multiple Responses

```yaml
scenario_2:
  multi_responses:
    - method: GET
      url: https://api.example.com/1
      body: one
    - method: GET
      url: https://api.example.com/2
      body: two
```

### Native Responses Files

Provide a filename string to load a native Responses YAML/JSON file.

```yaml
scenario_3:
  native_responses: responses_replay.yaml
```

## Advanced Usage

### Overriding Responses

Use `psf_responses.replace()` or `upsert()` in the test or a fixture to
modify loaded mocks.

```python
@pytest.fixture
def auth_error(psf_responses):
    psf_responses.replace("GET", "https://api.example.com/data", status=401)
    return psf_responses


def test_api(auth_error):
    resp = requests.get("https://api.example.com/data")
    assert resp.status_code == 401
```

### With `psf_expected_result`

Combine Responses mocks with `psf_expected_result_indirect` to test both
success and failure paths.

```yaml
failure_case:
  api_response:
    method: GET
    url: https://api.example.com/data
    status: 403
  psf_expected_result_indirect:
    expected_exception_name: requests.HTTPError
```

```python
def test_api(psf_responses, psf_expected_result):
    with psf_expected_result:
        resp = requests.get("https://api.example.com/data")
        resp.raise_for_status()
```

### Moto Integration

If using `moto`, you must call
`override_responses_real_send(psf_responses)` from `moto.core.models` to
allow Responses to catch the requests.
