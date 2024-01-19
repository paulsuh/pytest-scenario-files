# pytest-parameterize-from-files

.. image:: https://img.shields.io/pypi/v/pytest-parameterize-from-files.svg
    :target: https://pypi.org/project/pytest-parameterize-from-files
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-parameterize-from-files.svg
    :target: https://pypi.org/project/pytest-parameterize-from-files
    :alt: Python versions

.. image:: https://ci.appveyor.com/api/projects/status/github/paulsuh/pytest-parameterize-from-files?branch=master
    :target: https://ci.appveyor.com/project/paulsuh/pytest-parameterize-from-files/branch/master
    :alt: See Build Status on AppVeyor

A plugin that parameterizes tests from data files using the hook pytest_generate_tests

----


## Introduction

When you are using `pytest` you may have multiple inputs that you need to test against a particular
test function. Pytest has a feature called parameterization, where fixtures can
can take on a series of values in order to run the same test function repeatedly
under different test cases. However, sometimes the input data is very large or there are
many cases, so that it is impractical to put all of the data into the source code
of the test.

This plug-in loads the data for the test parameterization from separate
data files that are automatically matched up against the test functions. Each
function can have one or more data files associated with it, and each file can
contain multiple test cases. The data files can be in JSON or YAML format.

An additional issue with the basic pytest parameterization API is the way the user must
provide the parameters. First all of the test case fixture names in a list,
followed by a list of lists with the
values the fixtures will take on, and then an optional list of test case id's. Since the labels,
values, and id's are in separate lists it can be difficult to keep track of which
fixture corresponds to which value if you have many of them, and also which
group of values corresponds to which test id. The file structure uses a dict to keep
the test id and the data values together.

## Features

- Loads data for tests from files
- Multiple data sets may be in one file
- There may be multiple data files for each test

## Requirements

- Tested with `pytest` version 7.4.x
- Tested with CPython 3.8 - 3.12 and PyPy 3.9

## Installation

You can install `pytest-parameterize-from-files` via `pip` from PyPI:

    $ pip install pytest-parameterize-from-files

## Usage

To use this plugin you need to make only two changes to your test code:
1. Create the data file(s) with the proper names and formats
2. Add the fixture `paramfiledata` to your test function

You can then access the data from the files via the `paramfiledata` fixture.
A common use case is to manage multiple test case inputs and outputs. This allows
the developer to change and add test cases without making changes to the test code.

### Data File Structure
Each data file may contain one or more sets of test data. This plugin supports
yaml, json, and toml files. The top level is a dict that contains a key with
the test id, followed by a data structure that contains the test data. The
actual content of the test data is left up to the developer, but the suggested
convention is that it consists of a dict with two keys, `input_data` and
`expected_result`. An example input file might be:

```yaml
test1:
  input_data:
    x: 17
    y: 3
  expected_result: 51

test2:
  input_data:
    x: 7
    y: 7
  expected_result: 49
```

This would parameterize into two test cases labeled `test1` and `test2`.

### File Matching
Data files will be loaded if they match both of the following criteria:
1. They are named for the test function, but swapping the prefix `test_`
    for the prefix `data_` (although the file names may be suffixed by any value).
2. They are contained in a folder at or below the file that contains the test.

For example, for a test function `test_foo(paramfiledata)`, the files
`data_foo_part_1.json` and `data_foo_part_2.yaml` would both be loaded.

Be careful of tests with extended names. If you have two tests, `test_foo()` and
`test_foo_bar()` in the same file, a data file with the name `data_foo_bar.yaml`
will be parameterized for *both* tests. To prevent this, split the two test
functions into two separate files in two different directories or change the name of one of the test
functions.

## Contributing
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the `MIT` license, "pytest-parameterize-from-files" is free and open source software


## Issues

If you encounter any problems, please `file an issue`_ along with a detailed description.

## Colophon

Inspired by pytest-datadirs, pytest-datafixtures, and pytest-xattr. This `pytest` plugin
was generated with `Cookiecutter` along with `@hackebrot`'s `cookiecutter-pytest-plugin`
template, then extensively modified to bring it up to modern standards.



- [Cookiecutter](https://github.com/audreyr/cookiecutter)
- [MIT License](http://opensource.org/licenses/MIT)
- [cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin)
- [file an issue](https://github.com/paulsuh/pytest-parameterize-from-files/issues)
- [pytest](https://github.com/pytest-dev/pytest)
