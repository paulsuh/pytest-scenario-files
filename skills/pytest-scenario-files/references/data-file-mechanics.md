# Data file mechanics: placement, naming, and fixture rules

Details referenced from the main skill body — read this when you need the
specifics behind "where does the plugin look" or "why did collection fail."

## Where to put the data files

The plugin finds a data file for `test_foo()` by walking the directory tree
**starting at the test file's own directory and searching downward** — same
directory, or any subdirectory beneath it. It will never find a file in a sibling
or parent directory. (This is specifically the auto-discovery search root —
`__file:case:fixture` cross-file references use a different root entirely; see
`references/cross-file-sharing.md`.) Two conventions are both valid; which one
fits depends on scale:

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
*references* covered in `references/cross-file-sharing.md` — this is unconditional,
automatic merging of every matching file, not an explicit pointer to one value in
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
