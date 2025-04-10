# pytest-scenario-files

***Making Pytest Scenarios Easy and Scalable***

![PyPI pyversions][link01] ![Pytest][link02]

![Hatch project][link03] ![Ruff][link04] ![Pre-Commit][link05]

[`pytest-scenario-files`][link06] is a [`pytest`][link07] plugin that
runs unit test scenarios using data loaded from files.

______________________________________________________________________

## Introduction

`pytest` has a feature called parameterization that allows you to run
the same test function repeatedly using different inputs to test
multiple scenarios. However, managing the test data for parameterization
can be a problem. Sometimes the input data is very large or there are
many test cases, so that it is impractical to put all of the data into
the source code of the test.

This plug-in loads the data for the test scenarios from separate data
files that are automatically matched up against the test functions. Each
function can have one or more data files associated with it, and each
file can contain multiple scenarios. The data files can be in JSON or
YAML format.

### Features

- Loads data for scenarios from files into fixtures
- Multiple scenario data sets may be in one file
- There may be multiple data files for each test
- Fixtures may refer to fixtures in other files
- Can specify indirect parameterization
- Intuitive and sane data file structure
- Integration with [Responses][link08]
- **NEW** - Integration with [Respx][link09]

### Compatibility

This package is a plug-in for `pytest` and works with Python 3.9 and up.

- Tested with `pytest` versions 7.4, 8.2, and 8.3.
- Tested with CPython 3.9-3.13.

### Documentation

For more information on advanced usages, read the
[detailed documentation][link10].

______________________________________________________________________

## Quickstart

### Installation

Install `pytest-scenario-files` from PyPI by using `pip` :

```
$ pip install pytest-scenario-files
```

### Add Fixtures

For each test where you want to have data loaded from a file, add the
name of a fixture to the list of arguments for the test. For instance,
if you have a target function:

```python
def foo(x):
    return 3 * x
```

And a test function:

```python
def test_foo():
    assert foo(17) == 51
```

You can set up `test_foo()` for scenarios by adding two fixtures:

```python
def test_foo(input_value, expected_result):
    assert foo(input_value) == expected_result
```

### Create a Data File

A data file will be loaded if it matches all of the following criteria:

1. The filename starts with `data_`, followed by the name of the test
   function with the prefix `test_` removed. The remainder of the
   filename may be any value, and is usually used to identify the tests
   contained in the file.
2. The filename must end in `.json`, `.yaml`, or `.yml`.
3. The file is contained in a folder at or below the file that contains
   the test.

For this example, create a YAML file with the name
`data_foo_scenarios_1.yaml`.

Inside the file, set up a structure with two levels of nested
dictionaries.

1. The top level is the name of each scenario.
2. The second level has the name of each fixture with value assignments.

```yaml
scenario_1:
  input_value: 17
  expected_result: 51
scenario_2:
  input_value: 7
  expected_result: 21
scenario_string:
  input_value: a
  expected_result: aaa
scenario_list:
  input_value:
    - x
  expected_result:
    - x
    - x
    - x
```

### Run the Tests

```shell
$ pytest -vv -rA
```

You will see the test run four times, each with a different input value
and expected result. (The option `-vv` gives verbose output; the option
`-rA` prints all logging and output from the tests. Neither is
necessary, but they're nice to have.)

______________________________________________________________________

## Reporting Issues

If you encounter any problems, please [file an issue][link11] including
a detailed description and (if possible) an example of the problem.

## License

Distributed under the terms of the `MIT` license,
`pytest-scenario-files` is free and open source software.

[link01]: https://img.shields.io/pypi/pyversions/pytest-scenario-files.svg
[link02]: https://img.shields.io/badge/Pytest-Plug--in-orange?logo=pytest
[link03]: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
[link04]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[link05]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
[link06]: https://github.com/paulsuh/pytest-scenario-files
[link07]: https://docs.pytest.org/en/stable/index.html
[link08]: https://github.com/getsentry/responses/tree/master
[link09]: https://github.com/lundberg/respx/tree/master
[link10]: https://pytest-scenario-files.mspex.net/
[link11]: https://github.com/paulsuh/pytest-scenario-files/issues
