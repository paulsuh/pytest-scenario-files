# responses vs. respx: key differences

Both integrations load HTTP mock data from scenario files, but `respx` (for
`httpx`) uses slightly different field names and has one important mechanical
difference from `responses` (for `requests`). If you're only using one of the
two, you probably don't need this file — it's for switching between them or
supporting both in the same project.

## Field name differences

| Responses key | Respx key |
|---|---|
| `status` | `status_code` |
| `body` | `text` |
| `content_type` (function arg) | `content_type` (header) |

`json` is spelled the same in both and is mutually exclusive with `body`/`text`.

## Fixture and flag differences

| | Responses | Respx |
|---|---|---|
| Fixture | `psf_responses` | `psf_respx_mock` |
| Activation flag | `--psf-load-responses` | `--psf-load-respx` |
| Extra dependency | `pytest-scenario-files[responses]` | `pytest-scenario-files[respx]` |
| Require every mock called | `--psf-fire-all-responses` | `--psf-assert-all-called` |
| Reject unmocked calls | (not available) | `--psf-assert-all-mocked` |

## Replacing a mocked response

- **Responses**: `responses.RequestsMock` has an `upsert(**kwargs)` method —
  replaces an existing mock for the same method/URL, or adds one if there's no
  match. This is what makes the override pattern in the main skill body
  (a `response_override` fixture wrapping `psf_responses`) a one-line call.
- **Respx**: there is no equivalent `upsert()`/`replace()` method. To override a
  response, register a new route for the same method and URL — the new route
  registration itself replaces the old one:

  ```python
  @pytest.fixture
  def response_override(request, psf_respx_mock):
      if hasattr(request, "param") and isinstance(request.param, dict):
          override = request.param.copy()
          route_match = {k: override.pop(k) for k in ("method", "url")}
          psf_respx_mock.route(**route_match).respond(**override)
      return psf_respx_mock
  ```

## Multiple responses for the same method and URL

- **Responses**: automatically queues successive responses to the same
  method/URL and returns them to the caller in order — just list them in
  sequence in the data file.
- **Respx**: does not queue automatically. To get sequential responses to the
  same method/URL, they must be specified explicitly (the plugin builds this
  from a list of responses under the same fixture, setting up `side_effect`
  under the hood) rather than relying on request-order queuing.
