# Advanced Usage

## Test Case Merging

If the same test ID appears in multiple files, their fixtures are
merged.

- **Success**: `data_1.yaml` defines `fixture_a`, `data_2.yaml` defines
  `fixture_b`. The test receives both.
- **Conflict**: If both files define the same fixture name for the same
  test ID, an exception is raised.

## Loading by Reference

Load a fixture value from another data file using the format:
`__filename:test_id:fixture_name`.

```yaml
# data_check.yaml
check_data:
  input: 42
  other_data: __data_foo.yaml:test_case_one:fixture_two
```

## Indirect Parameterization

To use
[indirect parameterization](https://docs.pytest.org/en/stable/example/parametrize.html#indirect-parametrization),
append `_indirect` to the fixture name in the data file. The value is
passed to a fixture function, and its return value is passed to the
test.

```yaml
# data_file.yaml
test1:
  val_indirect: 3
```

```python
@pytest.fixture
def val(request):
    return request.param * 10


def test_func(val):
    assert val == 30
```

**Note:** If using `autouse` fixtures with indirect parameterization,
every scenario must provide a value (even `null`) to avoid
`request.param` errors.

## The `psf_expected_result` Fixture

Supports
[Parameterized Conditional Raising](https://docs.pytest.org/en/stable/how-to/parametrize.html#parametrizing-conditional-raising)
by wrapping either an expected exception or a result value in a context
manager.

```python
def test_some_function(psf_expected_result):
    with psf_expected_result as expected:
        assert expected == some_function()
```

In the data file, use `psf_expected_result_indirect`:

- **For Exceptions**: Use a dictionary with `expected_exception_name`
  (full identifier) and optional `match` string/regex.
- **For Values**: Use any other value (string, number, or dict without
  `expected_exception_name`).

```yaml
failure_scenario:
  psf_expected_result_indirect:
    expected_exception_name: requests.HTTPError
    match: Authorization failure

success_scenario:
  psf_expected_result_indirect: expected result string
```
