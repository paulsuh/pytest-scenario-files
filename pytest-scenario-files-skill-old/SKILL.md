______________________________________________________________________

name: pytest-scenario-files

## description: A pytest plugin that automates loading test scenarios from JSON/YAML files into parameterized fixtures. Use it when test data is too large for source code, to separate data from logic, or to reuse data across tests via file-based references.

# pytest-scenario-files

`pytest-scenario-files` is a `pytest` plugin that runs unit test
scenarios using data loaded from files. It makes managing large amounts
of test data easier by separating it from the test code.

## Core Features

- Loads data for scenarios from files into fixtures.
- Data files are matched with tests by a naming convention.
- Multiple scenario data sets may be in one file.
- Fixtures may refer to fixtures in other files.
- Supports indirect parameterization.
- Integration with Responses and Respx mocking packages.

## Installation

This plug-in can be installed from PyPI using `pip`:

```bash
pip install pytest-scenario-files
```

If you want to utilize the Responses or Respx integration, specify the
corresponding extra:

```bash
pip install pytest-scenario-files[responses]
pip install pytest-scenario-files[respx]
```

## Basic Usage

To use `pytest-scenario-files`, add fixtures to your test function
arguments and create matching data files.

Each fixture must be present in the test function's argument list:

```python
def test_foo(input_data_1, input_data_2, expected_result):
    assert expected_result == foo(input_data_1, input_data_2)
```

### Data File Structure

Data files (YAML or JSON) are dictionaries where keys are test IDs, and
values are dictionaries mapping fixture names to data.

```yaml
# data_foo_1.yaml
test1:
  input_data_1: 17
  input_data_2: 3
  expected_result: 51

test2:
  input_data_1: [abc]
  input_data_2: 3
  expected_result: [abc, abc, abc]
```

**Note:** Every scenario for a test must define the same set of
fixtures. Use `null` or empty strings if a fixture is unused in a
specific scenario.

### Integrating With Regular Fixtures

If a fixture is defined in code (e.g., `conftest.py`), it does not need
to be in the data file.

```python
@pytest.fixture
def input_data_2():
    return 5


# data_foo_1.yaml only needs input_data_1 and expected_result
```

### Data File Matching

Files must end in `.json`, `.yaml`, or `.yml`. A file is loaded for
`test_name()` if:

1. The filename starts with `data_` followed by the test name (minus
   `test_`).
2. The file is in the same directory as the test or a subfolder.

Example for `test_foo()`: `data_foo_part_1.json`,
`subfolder/data_foo.yaml`.

### Caution: Name Conflicts

If one test name is an extension of another (e.g., `test_foo` and
`test_foo_bar`), a data file named `data_foo_bar.yaml` will be loaded
for **both** tests. To avoid this, use unique names or separate
directories.

## When to use this skill

Use this skill when you need to:

- Understand how `pytest-scenario-files` works.
- Set up or configure the plugin.
- Create or debug data files for test scenarios.
- Use advanced features like loading by reference or indirect
  parameterization.
- Integrate with Responses or Respx for HTTP mocking in scenarios.

## Reporting Issues

If you encounter any problems, please
[file an issue](https://github.com/paulsuh/pytest-scenario-files/issues)
including a detailed description and an example of the problem.

## Reference Documentation

Detailed documentation is available in the `references/` directory:

- [Advanced Usage](references/advanced_usage.md): Merging test cases,
  loading by reference, and the `psf_expected_result` fixture.
- [Responses Integration](references/responses_integration.md): Detailed
  guide on using Responses with scenario files.
- [Respx Integration](references/respx_integration.md): Detailed guide
  on using Respx with scenario files.
