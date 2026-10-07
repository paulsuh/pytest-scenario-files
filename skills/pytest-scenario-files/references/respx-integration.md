# Respx integration (HTTP mocking for `httpx`)

Covers the `psf_respx_mock` fixture, backed by the `respx` package, for
mocking `httpx`-based HTTP calls from scenario data. If your project uses
`requests` instead, see `references/responses-integration.md`.

Note the respx integration uses slightly different field names than
`responses` (`status_code` instead of `status`, `text` instead of `body`).

## Activation

Naming a fixture `..._response`/`..._responses` in a data file isn't enough on
its own — the `psf_respx_mock` integration only activates when you pass
`--psf-load-respx`. Without the flag, a `_responses` key is treated as
ordinary scenario data, not extracted into an HTTP mock, and `psf_respx_mock`
won't be available as a fixture at all. In practice, set the flag once via
`addopts` rather than typing it every run:

```ini
# pytest.ini or [tool.pytest.ini_options] in pyproject.toml
addopts = --psf-load-respx
```

`--psf-assert-all-called` fails the test if a mocked response never gets
called; `--psf-assert-all-mocked` fails the test if a request goes out that
wasn't mocked.

Install with the `respx` extra: `pytest-scenario-files[respx]`.

`--psf-load-responses` and `--psf-load-respx` are mutually exclusive — passing
both raises a `pytest.UsageError`.

## Combining psf_expected_result with psf_respx_mock: override, don't duplicate

When most of your scenarios share the same successful HTTP response and only a
handful of scenarios need it to fail differently, don't copy the full
`http_responses` list into every scenario with one field changed — that's the
same "disguised duplication" problem as anywhere else in a data file, and it
means the shared response can drift out of sync between scenarios. Instead:

1. Put the common response in a shared file, loaded by reference into every
   scenario (or via a YAML anchor, if it's all in one file) — see
   `references/cross-file-sharing.md`.
2. Give only the scenarios that need something different a `..._override_indirect`
   fixture describing the change (usually just the URL/method plus the status
   and body that make this scenario fail).
3. Write one fixture, layered on top of `psf_respx_mock`, that applies the
   override if present and passes the mock through unchanged if not.
4. Pair it with `psf_expected_result_indirect` so the same test body checks the
   success value in the common case and the exception in the overridden case.

```yaml
# data_api_check.yaml
success_scenario:
  api_responses: __data_api_common.yaml:defaults:api_responses
  psf_expected_result_indirect: "the call was successful"

failure_scenario:
  api_responses: __data_api_common.yaml:defaults:api_responses
  response_override_indirect:
    url: https://api.example.com/v1/endpoint
    method: GET
    status_code: 403
    text: "access denied"
  psf_expected_result_indirect:
    expected_exception_name: requests.exceptions.HTTPError
```

```python
@pytest.fixture
def response_override(request, psf_respx_mock):
    if hasattr(request, "param") and isinstance(request.param, dict):
        override = request.param.copy()
        route_match = {k: override.pop(k) for k in ("method", "url")}
        psf_respx_mock.route(**route_match).respond(**override)
    return psf_respx_mock


def test_api_check(response_override, psf_expected_result):
    with psf_expected_result as expected_result:
        result = requests.get("https://api.example.com/v1/endpoint")
        result.raise_for_status()
        assert result.text == expected_result
```

There is no `upsert()`/`replace()` method for respx. To override a response,
register a new route for the same method and URL — the new route registration
itself replaces the old one.

## Repeated calls to the same URL: sequential responses and polling

Putting more than one response entry under the same fixture with the same
method and URL isn't a mistake — the plugin loads them so successive calls to
that URL get each response in order. This is the natural way to express a
polling loop in a data file: a status-check endpoint that returns "still
running" a few times before returning "done":

```yaml
polling_scenario:
  api_responses:
    - method: GET
      url: https://api.example.com/v1/jobs/123
      status_code: 202
      json: {status: "running"}
    - method: GET
      url: https://api.example.com/v1/jobs/123
      status_code: 202
      json: {status: "running"}
    - method: GET
      url: https://api.example.com/v1/jobs/123
      status_code: 200
      json: {status: "done"}
```

The list of responses under one fixture is turned into a `side_effect`
sequence — order is guaranteed within one list, but not between separate
response lists sharing the same URL if you split them across files. Once a
list is exhausted, the next call raises `StopIteration` — there's no built-in
way to say "repeat the last response forever." If a test genuinely needs
unbounded repetition (e.g. an infinite polling loop under test), write your
own override fixture using `itertools.chain()`/`itertools.repeat()` rather
than relying on the data file alone.

There is no Respx equivalent of Responses' native-save-file loading
(see `references/responses-integration.md`).
