# Contributing to pytest-scenario-files itself

This file is for anyone modifying `pytest-scenario-files`' own source
(`src/pytest_scenario_files/plugin.py`) and needing to write or update tests in
*this* repository. It does not apply to a project that merely depends on the
plugin — see `../SKILL.md` for that.

## Test-driven development is required, and tests must use `pytester`

Since this project is a pytest plugin, its own tests can't just call functions
directly — they need to run a real, isolated pytest session and check its outcome.
Every test under `tests/basic cases/` follows the same shape, built on pytest's
built-in `pytester` fixture:

1. Copy a template test module into the (isolated, temp-directory) test run with
   `pytester.copy_example("example_test_<name>.py")`, then `.rename(...)` it into
   its final location. Templates live in `tests/pytester_example_files/`.
2. Copy the data file(s) the same way: `pytester.copy_example("data_<name>.yaml")`,
   `.rename(...)` if it needs to land in a subdirectory.
3. Run the nested pytest session: `pytester.runpytest("-k", "test_name", "-v", ...)`.
4. Assert on the outcome: `result.assert_outcomes(passed=N)` for success cases,
   `result.assert_outcomes(errors=N)` plus `result.stdout.fnmatch_lines([...])` for
   failure cases that need to check the actual error message.

```python
def test_load_one_file(pytester):
    test_file_path = pytester.copy_example("example_test_load_one_file_tester.py")
    test_file_path.rename("test_load_one_file_tester.py")

    pytester.copy_example("data_load_one_file_tester.json")

    result = pytester.runpytest("-k", "test_load_one_file_tester", "-v")

    result.assert_outcomes(passed=1)
```

Stick to this convention rather than hand-writing test/data file contents inline in
the test function body — reusing the shared `pytester_example_files/` templates
keeps new tests visually consistent with the existing suite, and means a template
used by several tests only needs to be understood once. The only time inline content
is appropriate is when a value is inherently dynamic and can't be known until the
test runs (e.g. a path generated from `pytester.path`) — in that case, still start
from the copied/renamed template and append the dynamic piece to it, rather than
writing the whole file body by hand.

## Verifying changes without `hatch`/`pre-commit`

The project's own contributing docs point at `hatch test --all`, `hatch run cov`, and
`pre-commit run --all-files`. Those need network access to build hatch's isolated
environments and pre-commit's hook environments. If that's unavailable (a sandboxed
or offline session), verify directly instead:

```bash
PYTHONPATH="$(pwd)/src" pytest tests -v
```

The `PYTHONPATH` override matters: if this project's `.venv` has an installed copy of
`pytest_scenario_files` (e.g. installed non-editably, or stale relative to a recent
`src/` change), tests will silently run against *that* copy instead of your working
tree, and a change to `plugin.py` won't show up in the results at all. Prepending
`src/` on `PYTHONPATH` forces Python to import your working copy first.

For linting, if `.ruff_cache/` under the repo isn't writable in your environment:

```bash
RUFF_CACHE_DIR="$TMPDIR/ruff_cache" ruff check src tests
RUFF_CACHE_DIR="$TMPDIR/ruff_cache" ruff format --check src tests
```

## `tests/conftest.py` silently skips `basic cases/` in some environments

```python
from importlib.util import find_spec

pytest_plugins = "pytester"

if (find_spec("responses") is not None) or (find_spec("respx") is not None):
    collect_ignore_glob = ["basic cases/*"]
```

If either `responses` or `respx` is importable in the active environment — which is
common, since they're often installed for the `responses integration/`/
`respx integration/` test suites — the **entire** `tests/basic cases/` tree is
skipped from collection. This tree holds all of the core data-loading, merging, and
reference-resolution tests. A green `pytest tests` run in an environment with those
packages installed proves nothing about that core logic.

If you're testing a change to core loading behavior, either run in an environment
without `responses`/`respx` installed, or temporarily neutralize the condition
(e.g. `if False and (...)`) to force collection — and make sure to revert that
before committing.
