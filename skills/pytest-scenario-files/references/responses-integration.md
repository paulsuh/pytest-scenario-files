# Responses integration (HTTP mocking for `requests`)

Covers the `psf_responses` fixture, backed by the `responses` package, for
mocking `requests`-based HTTP calls from scenario data. If your project uses
`httpx` instead, see `references/respx-integration.md`.

## Activation

Naming a fixture `..._response`/`..._responses` in a data file isn't enough on
its own — the `psf_responses` integration only activates when you pass
`--psf-load-responses`. Without the flag, a `_responses` key is treated as
ordinary scenario data, not extracted into an HTTP mock, and `psf_responses`
won't be available as a fixture at all. In practice, set the flag once via
`addopts` rather than typing it every run:

```ini
# pytest.ini or [tool.pytest.ini_options] in pyproject.toml
addopts = --psf-load-responses
```

`--psf-fire-all-responses` fails the test if a mocked response never gets
called.

Install with the `responses` extra: `pytest-scenario-files[responses]`.

If you're mocking AWS with `moto` alongside `psf_responses` for other HTTP
calls, note that `moto` installs its own `RequestsMock` under the hood, which
will swallow your mocked responses unless you call
`moto.core.models.override_responses_real_send(psf_responses)` at the top of
the test (per moto's own FAQ) — otherwise your `psf_responses` mocks silently
never fire.

## Combining psf_expected_result with psf_responses: override, don't duplicate

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
3. Write one fixture, layered on top of `psf_responses`, that applies the
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
    status: 403
    body: "access denied"
  psf_expected_result_indirect:
    expected_exception_name: requests.exceptions.HTTPError
```

```python
@pytest.fixture
def response_override(request, psf_responses):
    if hasattr(request, "param") and isinstance(request.param, dict):
        psf_responses.upsert(**request.param)  # replaces the matching mock, or adds a new one
    return psf_responses


def test_api_check(response_override, psf_expected_result):
    with psf_expected_result as expected_result:
        result = requests.get("https://api.example.com/v1/endpoint")
        result.raise_for_status()
        assert result.text == expected_result
```

`responses.RequestsMock.upsert()` replaces an existing mock for the same
method/URL or adds one if there wasn't a match — that's what lets a scenario
override just the one response it cares about.

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
      status: 202
      json: {status: "running"}
    - method: GET
      url: https://api.example.com/v1/jobs/123
      status: 202
      json: {status: "running"}
    - method: GET
      url: https://api.example.com/v1/jobs/123
      status: 200
      json: {status: "done"}
```

A single response registered for a URL is returned to every call, while a
list is consumed in order. Once the list is exhausted, the next call raises
`StopIteration` — there's no built-in way to say "repeat the last response
forever." If a test genuinely needs unbounded repetition (e.g. an infinite
polling loop under test), write your own override fixture using
`itertools.chain()`/`itertools.repeat()` rather than relying on the data file
alone.

## Loading a native Responses save file

If a `..._response`/`..._responses` fixture's value is a plain string rather
than a dict or list, the plugin treats it as the filename of a file already in
`responses`' own native save format (as produced by `RequestsMock._dump()` or
similar tooling) and loads it via Responses' own file-loading mechanism, in
addition to any other responses defined alongside it. This has no Respx
equivalent. Unlike a normal `data_*` file (which searches downward from the
test's own directory), this native file is searched from the current working
directory, so a stray duplicate of that filename anywhere under cwd raises an
error rather than silently picking one:

```yaml
scenario_3:
  native_file_responses: responses_replay_data.yaml
```
