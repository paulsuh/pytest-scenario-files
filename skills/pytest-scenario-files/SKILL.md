---
name: pytest-scenario-files
description: >
  Guidance for using the pytest-scenario-files plugin to drive pytest tests from
  YAML/JSON data files. Use this whenever writing or refactoring pytest tests that
  have multiple scenarios, involve test data files, mock HTTP calls with responses
  or respx, or need parameterization that scales past a handful of cases — even if
  the user doesn't mention "pytest-scenario-files" by name and just says things like
  "add more test cases," "this test file is getting unwieldy," "mock these API
  calls," or "turn this into a data-driven test." This is an addendum to general
  pytest/testing skills, not a replacement — defer to those for test design,
  mocking philosophy, and coverage strategy; this skill covers only what
  pytest-scenario-files specifically brings: data-file mechanics, the YAML-vs-inline
  judgment call, and this plugin's particular gotchas.
---

# pytest-scenario-files

## What this plugin does and doesn't replace

`pytest-scenario-files` auto-discovers a data file next to a test function, loads it,
and parameterizes the test from it — no `@pytest.mark.parametrize` decorator, no
manual file-reading code. It exists to fix one specific pain point: handwritten
`parametrize` calls require three parallel lists (fixture names, a list of value-lists,
and optional test ids), and keeping them in sync gets hard once you have more than a
few scenarios or the values are bulky. A YAML/JSON file keeps the case id, fixture
names, and values together in one dict, which is easier to read and maintain.

That's the whole scope. This skill is not a general guide to test design, mocking
strategy, or coverage — use whatever pytest/testing skill or convention your project
already follows for those. Reach for this skill specifically when the question is
"should this scenario data live in a file, and if so, how should I structure it."

## When to reach for a data file vs. keeping things inline

This is a judgment call, not a hard rule — think of it as a spectrum.

**Reach for a YAML/JSON data file when:**
- You have 2+ scenarios that share the same fixture shape (same set of fixture names,
  different values).
- The data itself is bulky or nested (a multi-call HTTP mock sequence, a large
  expected-result structure).
- You want scenario data to be diffable and editable without touching test code —
  useful if teammates who aren't deep in the test file need to add cases.

**Keep it inline (a plain `@pytest.fixture` or `@pytest.mark.parametrize`) when:**
- You have exactly one scenario. A data file plus the plugin's machinery buys you
  nothing over a simple fixture:

  ```python
  # Don't do this for a single scenario
  @pytest.mark.parametrize("test_data", [{"expected": "result"}])
  def test_single_case(test_data):
      assert function() == test_data["expected"]

  # Do this instead
  @pytest.fixture
  def expected_result():
      return "result"

  def test_single_case(expected_result):
      assert function() == expected_result
  ```

- The value can't be expressed as YAML/JSON — a callable, a class instance, or a
  `pytest.param(..., marks=pytest.mark.xfail)`. `_indirect` fixtures (see below) are
  the escape hatch when you need parameterized *data* to produce a constructed object.
- The value doesn't actually vary across scenarios. If every scenario defines the
  same value for a fixture, it's not scenario data — it's a regular fixture. Just omit
  it from the data file and define it normally in the test file or `conftest.py`; the
  plugin only supplies the fixtures a data file defines, so a fixture from `conftest.py`
  composes fine alongside scenario data for the *other* fixtures a test takes.

A concrete antipattern worth naming: a data file with exactly one scenario, holding
only plain scalar constants (e.g. a handful of config values asserted against module
constants). This adds a file, an indirection, and a second copy of the same values,
without buying any parameterization. If nothing varies and there's only one case,
inline constants are more honest about what the test is doing.

## Where to put the data files

The plugin finds a data file for `test_foo()` by walking the directory tree
**starting at the test file's own directory and searching downward** — same
directory, or any subdirectory beneath it. It will never find a file in a sibling
or parent directory. Two conventions are both valid; which one fits depends on scale:

- **Colocated** — the data file sits right next to the test `.py` file. Simplest,
  and what the plugin's own docs assume. Fine for a small test module with a handful
  of data files.
- **Subdirectory** — data files live under a nested folder (commonly named
  `unit_test_data/` or `test_data/`, often mirroring the source package structure
  underneath, e.g. `unit_test_data/<module>/`). This is what larger suites converge
  on once a test directory accumulates many data files across many test modules —
  it keeps the directory listing of `.py` files readable. Because the search is
  downward-only, this still works without any extra configuration; the plugin finds
  `unit_test_data/<module>/data_foo.yaml` from `test_foo.py` sitting above it.

Rule of thumb: start colocated. Once a test directory holds more than a handful of
data files, or multiple test modules want to share a common data file, introduce a
subdirectory. There's no fixed threshold — ask what makes the directory easiest for
a human to scan.

## The filename-prefix trap

A data file matches by **filename prefix**, not exact name: it must start with
`data_` followed by the test function's name (minus the `test_` prefix), with
anything after that ignored, and end in `.json`/`.yaml`/`.yml`. This means
`test_foo()` and `test_foo_bar()` **both** match a file named `data_foo_bar.yaml`,
because `"foo_bar".startswith("foo")`. If you have two test functions whose names
share a prefix, put them in separate subdirectories (each one still findable by the
downward-only search) rather than relying on exact-name intuition:

```
tests/
  subdir1/
    test_foo.py
    data_foo.yaml
  subdir2/
    test_foo_bar.py
    data_foo_bar.yaml
```

## Missing or malformed data files are collection-time errors, not silent skips

If a test function expects scenario data but the search finds no matching file
at all — commonly because a test or its data file got renamed and the other
side wasn't updated — pytest reports it as an **error** at collection time, not
a skip and not a quiet pass with zero parameters. Similarly, a stray file that
happens to match the filename prefix but has the wrong extension (e.g. a
`data_foo_notes.txt` left next to `data_foo.yaml` for scratch notes) also
errors at collection, because the prefix match happens before the extension is
checked. Both are worth knowing so you read "1 error" in test output as "check
your data file naming," not as an unrelated collection failure.

## Every scenario needs every fixture key — and the better escape hatches than `null`

The plugin turns your data file into a `metafunc.parametrize()` call under the hood,
which requires every scenario (every "row") to supply a value for every fixture
("column") the test function takes. If one scenario doesn't have a meaningful value
for a fixture, you still have to include the key — with `null` if nothing else fits.

The tempting failure mode: a test function accumulates fixtures like
`should_raise_error`, `expected_error_message`, and four or five `expected_*` result
fields, and every error-path scenario ends up `null`-padding most of them because
only one or two keys are actually relevant to that branch. This is a signal to
restructure, not just a fact of life:

- **Narrow the test function** to only the fixtures it actually uses. If a fixture
  isn't referenced in the test body, drop it from both the signature and the data
  file.
- **Split into a second test function** if two branches need genuinely different
  mock setup (different `mocker.patch` targets, different fixture dependencies) —
  that's usually a sign they were never really one test.
- **Use `psf_expected_result_indirect`** to collapse a `should_raise_error` +
  `expected_error_message` + `if/else` branch into a single fixture:

  ```yaml
  success_scenario:
    psf_expected_result_indirect: "the returned value"

  failure_scenario:
    psf_expected_result_indirect:
      expected_exception_name: ValueError
      match: "invalid input"
  ```

  ```python
  def test_something(psf_expected_result):
      with psf_expected_result as expected:
          assert expected == function_under_test()
  ```

  One context manager handles both the success and failure cases — no more paired
  `should_raise_error`/`expected_error_message` fixtures to null-pad, and no more
  `if should_raise_error: pytest.raises(...) else: assert ...` branch in the test
  body.

Note this "every fixture key" rule applies across *all* the files that end up
contributing to one test, not just within a single file — see the next section.

## Splitting one test's data across multiple files

A single test function can pull its scenario data from more than one matching
file. Every file whose name matches the test's naming rule gets loaded and
merged by scenario id: if two files both define a scenario called
`test_one`, the fixtures they each contribute are combined into one scenario,
as long as they don't both try to define the same fixture (that raises
`BadTestCaseDataException`, naming the file and the conflicting fixture).

This is a different feature from the `__file:case:fixture` cross-file
*references* covered later in this file — this is unconditional, automatic
merging of every matching file, not an explicit pointer to one value in
another file. It's useful for splitting a test's inputs from its expected
results, or grouping columns by concern:

```yaml
# data_foo_1.yaml — inputs
test_one:
  input_data_1: "blah"

# data_foo_2.yaml — more inputs
test_one:
  input_data_2: "meep"

# data_foo_3.yaml — expected results
test_one:
  expected_result: "blahmeep"
```

All three files match `test_foo` and merge into one scenario with all three
keys. Because the "every scenario needs every fixture key" rule applies to the
*merged* result, adding a new scenario to just one of the files (without
matching keys in the others) will fail the consistency check across the whole
set, not just within that one file.

## Caution: autouse fixtures don't mix well with `_indirect`

If an `_indirect` fixture is also marked `autouse=True`, pytest instantiates it
for *every* scenario of *every* test in scope — including scenarios that have
nothing to do with that fixture. Since indirect parameterization works by
handing the fixture a `request.param` pulled from the data file, every one of
those scenarios must supply the `_indirect` key (even `null`), or the fixture
raises before the test body even runs, because `request.param` won't exist.
If you inherit or review a project that combines the two, either add the key
everywhere it's needed, or guard the fixture itself:

```python
@pytest.fixture(autouse=True)
def some_indirect_fixture(request):
    if not hasattr(request, "param"):
        return default_value
    return request.param
```

Given the failure mode is easy to hit by accident and easy to miss until a
new scenario is added somewhere else in the suite, it's generally simplest to
avoid pairing `autouse=True` with `_indirect` fixtures in the first place.

## The exception key is `expected_exception_name` — not `expected_exception_type`

Some versions of this plugin's own documentation describe the exception-matching key
under `psf_expected_result_indirect` as `expected_exception_type`. **That's wrong.**
The actual key the code checks for is `expected_exception_name`, as shown in the
example above. If a scenario using `expected_exception_type` doesn't raise the
expected `pytest.raises()`, this mismatch is the first thing to check. For a
non-builtin exception, use the fully-qualified dotted path (e.g.
`requests.exceptions.HTTPError`); builtins are looked up by bare name (e.g.
`ValueError`).

## HTTP mocking must be explicitly activated

Naming a fixture `..._response`/`..._responses` in a data file isn't enough on
its own — the `psf_responses`/`psf_respx_mock` integration only activates when
you pass `--psf-load-responses` or `--psf-load-respx` (mutually exclusive;
passing both raises a `pytest.UsageError`). Without the flag, a `_responses`
key is treated as ordinary scenario data, not extracted into an HTTP mock, and
`psf_responses`/`psf_respx_mock` won't be available as fixtures at all. In
practice, set the flag once via `addopts` rather than typing it every run:

```ini
# pytest.ini or [tool.pytest.ini_options] in pyproject.toml
addopts = --psf-load-responses
```

A few related flags round out the strictness knobs — `--psf-fire-all-responses`
(Responses) and `--psf-assert-all-called`/`--psf-assert-all-mocked` (Respx) fail
the test if a mocked response never gets called, or if a request goes out that
wasn't mocked. See `references/http-mocking-key-differences.md` for the full
flag comparison between the two integrations.

If you're mocking AWS with `moto` alongside `psf_responses` for other HTTP
calls, note that `moto` installs its own `RequestsMock` under the hood, which
will swallow your mocked responses unless you call
`moto.core.models.override_responses_real_send(psf_responses)` at the top of
the test (per moto's own FAQ) — otherwise your `psf_responses` mocks silently
never fire.

## Combining psf_expected_result with psf_responses/psf_respx_mock: override, don't duplicate

When most of your scenarios share the same successful HTTP response and only a
handful of scenarios need it to fail differently, don't copy the full
`http_responses` list into every scenario with one field changed — that's the
same "disguised duplication" problem as anywhere else in a data file, and it
means the shared response can drift out of sync between scenarios. Instead:

1. Put the common response in a shared file, loaded by reference into every
   scenario (or via a YAML anchor, if it's all in one file).
2. Give only the scenarios that need something different a `..._override_indirect`
   fixture describing the change (usually just the URL/method plus the status
   and body that make this scenario fail).
3. Write one fixture, layered on top of `psf_responses`/`psf_respx_mock`, that
   applies the override if present and passes the mock through unchanged if not.
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
override just the one response it cares about. For `psf_respx_mock`, the
equivalent fixture calls `respx_mock.route(method=..., url=...).respond(...)`
with the override's fields instead. Note the respx integration uses slightly
different field names than responses (`status_code` instead of `status`, `text`
instead of `body`) — check `references/http-mocking-key-differences.md` if
you're switching between the two.

## Repeated calls to the same URL: sequential responses and polling

Putting more than one response entry under the same fixture with the same
method and URL isn't a mistake — the plugin loads them so successive calls to
that URL get each response in order. This is the natural way to express a
polling loop in a data file: a status-check endpoint that returns "still
running" a few times before returning "done." (Shown here with respx's
`status_code` key — swap in `status` for the `responses` integration; see
`references/http-mocking-key-differences.md` for the rest of the field-name
differences.)

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

With `responses`, a single response registered for a URL is returned to every
call, while a list is consumed in order. With `psf_respx_mock`, the same list
is turned into a `side_effect` sequence — order is guaranteed within one list,
but not between separate response lists sharing the same URL if you split them
across files. Either way, once a list is exhausted, the next call raises
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
addition to any other responses defined alongside it. This is Responses-only —
there's no Respx equivalent. Unlike a normal `data_*` file (which searches
downward from the test's own directory), this native file is searched from the
current working directory, so a stray duplicate of that filename anywhere
under cwd raises an error rather than silently picking one:

```yaml
scenario_3:
  native_file_responses: responses_replay_data.yaml
```

## Cross-file sharing: anchors vs. `__file:case:fixture` references

Two independent mechanisms exist for avoiding duplicated data, and they solve
different scopes:

- **YAML anchors/aliases** (`&name` / `*name`) — plain YAML, dedupes *within one
  file*. Define the shared block once on the first scenario, reference it from
  later scenarios in the same file:

  ```yaml
  scenario_one:
    mock_env_vars: &shared_env
      API_KEY: test-key
    expected_result: "one"

  scenario_two:
    mock_env_vars: *shared_env
    expected_result: "two"
  ```

- **Cross-file references** — a string value prefixed with two underscores,
  `__filename.yaml:case_id:fixture_name`, resolved by the plugin at load time. Useful
  for sharing a block *across* multiple data files, commonly by pulling several
  files' worth of scenarios from one `data_<module>_common.yaml`:

  ```yaml
  # data_foo_common.yaml
  common:
    base_url: https://api.example.com

  # data_foo_client.yaml
  scenario_one:
    base_url: __data_foo_common.yaml:common:base_url
  ```

  Reference resolution searches **from the current working directory** (i.e.
  wherever `pytest` was invoked), not from the referencing file's own directory —
  so a reference can reach a file anywhere in the project, not just nearby. There is
  no way to configure or restrict this search root in the current version of the
  plugin. Nothing prevents an infinite self-referential loop, so avoid a reference
  chain that could cycle back on itself.

Don't reference every field individually if you're pulling several values from a
common file — that defeats the point. Reference the values that are actually shared,
and keep scenario-specific values (expected results, error messages) local to the
file that uses them.

## What stays in Python, never YAML

Some things genuinely can't be expressed as data, and don't try to force them:

- **Mock object construction and wiring** — `MagicMock()` instances, `side_effect`
  closures, `__enter__`/`__exit__` context-manager protocol setup. YAML can express
  the *values* a mock should return; it can't express object identity or protocol
  methods.
- **`mocker.patch(...)` target strings** — these name a code path to intercept, not
  scenario data.
- **Errors below the HTTP layer** — if you're using `psf_responses`/`psf_respx_mock`
  to mock HTTP calls, those fixtures mock a *response*. A raw transport-level
  exception (e.g. a `ConnectionError` that never produces an HTTP response at all)
  has to be injected with `mocker.patch(...).side_effect = ConnectionError(...)` —
  there's no response to describe in YAML.
- **Assertions about absence or call count** — `assert "field" not in result` or
  `mock.call_count == 1` describe an expectation about the code's behavior, not a
  scenario input.

A useful shape when a scenario needs several mock objects built from plain data:
factor the object-construction into one small helper that takes plain dicts/lists
(straight from the YAML fixture) and returns the wired-up mock:

```python
def _build_mock_engine(rows: list[dict]) -> MagicMock:
    """rows come straight from a YAML fixture; wiring stays here."""
    ...
```

This keeps the YAML holding only plain data, and isolates the "how do I make a fake
object behave like the real one" logic in exactly one reusable place instead of
repeating it per test.

## Validating what you generated — coverage vs. efficiency

After writing (or generating) a test and its data file, look at it with a critical
eye before considering it done. Coverage and efficiency pull in opposite directions —
more scenarios cover more cases, but each one costs upkeep — so both matter:

- **Fixture-key consistency** — every scenario in a data file must define the same
  set of keys. The plugin will raise `BadTestCaseDataException` at collection time if
  not, but catching it before running saves a cycle.
- **No filename-prefix collisions** with a sibling test function (see above).
- **No disguised duplication** — two data files with an identical fixture-key shape,
  each backing its own near-identical test function, are usually "one test, two
  scenarios" that never got merged. If you find yourself writing two test functions
  that differ only in the exception type they expect or one mocked value, that's a
  sign to consolidate into one test with two scenarios (using
  `psf_expected_result_indirect` to vary the exception).
- **Does the scenario count earn the file?** A single-scenario data file of plain
  constants is the sign to go back to a plain fixture (see above).
- **No orphaned data files** — if a test function was renamed or removed, its data
  file should go with it. An orphaned `data_*.yaml` that no test references anymore
  is easy to miss because nothing fails when it's just sitting there unused.

The efficiency judgment — "is this really 2 scenarios, or should these two test
functions be merged into one" — needs a human or model reading the test bodies.

## Sensitive-data caution

Moving a value from an inline Python constant into a YAML file makes it more visible
and more copy-pasteable — data files get grepped, diffed, and sometimes shared or
published more casually than test source code. Keep any hostname-, credential-, or
account-shaped value in a data file as an obvious placeholder
(`api.example.com`, `10.0.0.1`, `test-user`), never a real-looking internal identifier,
even in a private repo. If a test genuinely needs to assert a secret was handled
correctly, assert on its *presence* or *shape* rather than echoing the literal value
back out in the test body or a comment.

## Contributing to the plugin itself

Everything above is for people *using* pytest-scenario-files to write their own
project's tests. If you're modifying pytest-scenario-files' own source
(`plugin.py`) and need to write or update its pytest-based test suite, see
`references/contributing-to-plugin.md` instead — that covers the `pytester`-based
testing convention this project's own test suite follows, which is different from
how you'd write tests for a project that merely *depends on* this plugin.
