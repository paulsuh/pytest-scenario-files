# Advanced Usage

## Test Case Merging

If multiple files contain the same test case ID, their fixtures are
merged.

- **Example**: `data_foo_1.yaml` defines `fixture_one`, and
  `data_foo_2.yaml` defines `fixture_two` for `test_case_one`. The test
  receives both.
- **Conflict**: If the same fixture name is defined for the same test
  case ID in multiple files, an exception is raised.

## Loading Values by Reference

Load fixture data from another file using the `__` prefix:
`fixture_name: __Filename:test_case_id:fixture_name`

**Example**:

```yaml
check_logic:
  input: 42
  shared_config: __data_common.yaml:defaults:config
```

## Indirect Parameterization

Append `_indirect` to a fixture name in the data file to pass the value
to a fixture function instead of the test directly.

**Example**:

```yaml
test_case_1:
  val_indirect: 3
```

```python
@pytest.fixture
def val(request):
    return request.param * 10


def test_func(val):
    assert val == 30
```

## The `psf_expected_result` Fixture

A convenience fixture for handling both expected return values and
expected exceptions in the same test code.

**Usage in Test**:

```python
def test_logic(psf_expected_result):
    with psf_expected_result as expected:
        assert my_func() == expected
```

**Scenario Configuration**:

- **Exception**:
  ```yaml
  failure_case:
    psf_expected_result_indirect:
      expected_exception_name: ValueError
      match: Invalid input
  ```
- **Value**:
  ```yaml
  success_case:
    psf_expected_result_indirect: Success
  ```

*Note: Full identifiers (e.g., `requests.HTTPError`) should be used for
exceptions in modules.*
