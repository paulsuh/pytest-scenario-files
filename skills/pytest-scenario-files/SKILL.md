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
  `pytest.param(..., marks=pytest.mark.xfail)`. `_indirect` fixtures (see
  `references/data-file-mechanics.md`) are the escape hatch when you need
  parameterized *data* to produce a constructed object.
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

## Data file mechanics

Where files live, how they're matched, and the fixture-key rules governing a
scenario — including the collection-time error behavior for missing/malformed
files, the `_indirect` escape hatch, the autouse caveat, and splitting one
test's data across multiple files — are covered in
`references/data-file-mechanics.md`.

## HTTP mocking

`pytest-scenario-files` can extract HTTP mock data straight out of a scenario
file for either `requests` (via `responses`) or `httpx` (via `respx`). Each
integration has its own activation flag, fixture, and field names — see
whichever one your project uses:

- `references/responses-integration.md` — the `psf_responses` fixture,
  `--psf-load-responses`, override patterns, sequential/polling responses,
  and loading a native Responses save file.
- `references/respx-integration.md` — the `psf_respx_mock` fixture,
  `--psf-load-respx`, override patterns, and sequential/polling responses.

If you're using both integrations in the same project (or evaluating a third),
read both files — they use parallel structure so differences between them 
stand out.

## Cross-file sharing: anchors vs. `__file:case:fixture` references

Two independent mechanisms exist for avoiding duplicated data within and across
files — YAML anchors/aliases for within-file dedup, and `__filename.yaml:case:fixture`
references for across-file dedup. See `references/cross-file-sharing.md` for
syntax, search-root behavior, and when to use which.

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
- **No filename-prefix collisions** with a sibling test function (see
  `references/data-file-mechanics.md`).
- **No disguised duplication** — two data files with an identical fixture-key shape,
  each backing its own near-identical test function, are usually "one test, two
  scenarios" that never got merged. If you find yourself writing two test functions
  that differ only in the exception type they expect or one mocked value, that's a
  sign to consolidate into one test with two scenarios (using
  `psf_expected_result_indirect` to vary the exception).
- **Does the scenario count earn the file?** A single-scenario data file of plain
  constants is the sign to go back to a plain fixture (see above).

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
