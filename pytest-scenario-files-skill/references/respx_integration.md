# Respx Integration

Mock HTTP requests using the `respx` package (for `httpx`) by loading
data from scenario files.

## Differences from Responses

- Use the fixture `psf_respx_mock`.
- Activation flags: `--psf-load-respx`.
- Some key names differ (e.g., `status_code` instead of `status`).

## Basic Steps

1. **Fixtures**: Use names ending in `_response` or `_responses`.
2. **Parameter**: Pass `psf_respx_mock` to your test function.
3. **Flags**: Activate via `--psf-load-respx`.

## Data Format

```yaml
scenario_1:
  httpx_response:
    method: GET
    url: https://api.example.com/v1/user
    status_code: 200
    text: Success
    headers:
      content_type: text/plain
```

### Supported Keys

- `method`: GET, POST, PUT, etc. (Required)
- `url`: The endpoint to mock. (Required)
- `status_code`: HTTP status code.
- `text`: Text body (Mutually exclusive with `json`).
- `json`: Dictionary for JSON body.
- `headers`: Dictionary of headers (including `content_type`).

### Multiple Responses

If you provide a list of responses for the same method and URL, the
plugin will automatically configure Respx to return them sequentially
using `side_effect`.

## Command Line Options

- `--psf-load-respx`: Enables the integration.
- `--psf-assert-all-called`: Fails if any mock is not called.
- `--psf-assert-all-mocked`: Fails if any non-mocked HTTP call is made.

## Using `psf_respx_mock` in Tests

Returns a `respx.MockRouter` object.

```python
async def test_api(psf_respx_mock):
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/v1/user")
        assert response.status_code == 200
```
