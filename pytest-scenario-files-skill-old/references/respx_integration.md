# Respx Integration

Load HTTP responses from data files into the
[Respx](https://lundberg.github.io/respx/) package for mocking `httpx`
requests.

## Differences from Responses

- **Installation**: Use `pytest-scenario-files[respx]`.
- **Fixture**: Use `psf_respx_mock` (returns a `respx.MockRouter`).
- **Flags**: `--psf-load-respx`, `--psf-assert-all-called`,
  `--psf-assert-all-mocked`.
- **Response Keys**: Use `status_code` (not `status`) and `text` (not
  `body`).

## Basic Usage

1. **Enable**: Run pytest with `--psf-load-respx`.
2. **Fixture**: Add `psf_respx_mock` to your test. It is pre-loaded with
   scenario data.
3. **Data Format**: Define mocks in fixtures ending with `_response` or
   `_responses`.

### Single/Multiple Responses

```yaml
scenario_1:
  api_response:
    method: GET
    url: https://api.example.com/data
    status_code: 200
    json: {key: value}
    headers: {X-Test: foo}

scenario_2:
  multi_responses:
    - method: GET
      url: https://api.example.com/1
      text: one
    - method: GET
      url: https://api.example.com/1
      text: two    # Successive calls to same URL
```

## Advanced Usage

### Overriding Responses

Overwrite a loaded mock by setting a new route with the same method and
URL.

```python
def test_api(psf_respx_mock):
    # Override data file mock
    psf_respx_mock.route(method="GET", url="https://api.example.com/data").respond(
        status_code=401
    )

    with httpx.Client() as client:
        resp = client.get("https://api.example.com/data")
        assert resp.status_code == 401
```

### With `psf_expected_result`

Combine Respx mocks with `psf_expected_result_indirect`.

```yaml
failure_case:
  api_response:
    method: GET
    url: https://api.example.com/data
    status_code: 403
  psf_expected_result_indirect:
    expected_exception_name: httpx.HTTPStatusError
```

```python
def test_api(psf_respx_mock, psf_expected_result):
    with psf_expected_result:
        with httpx.Client() as client:
            resp = client.get("https://api.example.com/data")
            resp.raise_for_status()
```

### Sequential Responses

If multiple responses are defined for the same method/URL in a list,
they are returned in sequence. Once exhausted, further calls raise
`StopIteration`.
