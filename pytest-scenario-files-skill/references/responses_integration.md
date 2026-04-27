# Responses Integration

Mock HTTP requests using the `responses` package by loading data from
scenario files.

## Basic Steps

1. **Fixtures**: Use names ending in `_response` or `_responses`.
2. **Parameter**: Pass `psf_responses` to your test function.
3. **Flags**: Activate via `--psf-load-responses`.

## Data Format

Responses are defined as dictionaries or lists of dictionaries.

```yaml
scenario_1:
  api_response:
    method: GET
    url: https://api.example.com/v1/user
    status: 200
    json:
      id: 123
      name: John Doe
```

### Supported Keys

- `method`: GET, POST, PUT, etc. (Required)
- `url`: The endpoint to mock. (Required)
- `status`: HTTP status code (Default: 200).
- `body`: Text body (Mutually exclusive with `json`).
- `json`: Dictionary for JSON body.
- `content_type`: Content-Type header.
- `headers`: Dictionary of additional headers.

## Command Line Options

- `--psf-load-responses`: Enables the integration.
- `--psf-fire-all-responses`: If set, pytest will fail if any mocked
  response is not called.

## Using `psf_responses` in Tests

The fixture returns a `responses.RequestsMock` object.

```python
def test_api(psf_responses):
    # responses from files are already loaded
    response = requests.get("https://api.example.com/v1/user")
    assert response.status_code == 200
```

## Native Responses Files

You can reference a file in Responses' native format:

```yaml
scenario_3:
  legacy_responses: external_responses.yaml
```

The plugin will search for `external_responses.yaml` in the same way it
searches for data files.
