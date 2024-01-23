# pytest-parameterize-from-files

[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pytest-parameterize-from-files.svg)](https://pypi.python.org/pypi/pytest-parameterize-from-files/)

A [`pytest`](https://github.com/pytest-dev/pytest/) plugin that parameterizes
tests using data loaded from data files using the hook
[`pytest_generate_tests()`](https://docs.pytest.org/en/stable/reference/reference.html#collection-hooks).

----

## Introduction

When you are using `pytest` you may have multiple inputs that you need
to test against a particular test function. `pytest` has a feature called
parameterization, where fixtures can take on a series of values in order
to run the same test function repeatedly using different inputs to test
mulitple cases. However, sometimes the input data is very large or there
are many test cases, so that it is impractical to put all of the data into
the source code of the test.

This plug-in loads the data for the test parameterization from separate
data files that are automatically matched up against the test functions.
Each function can have one or more data files associated with it, and
each file can contain multiple test cases. The data files can be in JSON
or YAML format.

An additional issue with the basic pytest parameterization API is the
way the user must provide the parameters. First all of the test case
fixture names in a list, followed by a list of lists with the values the
fixtures will take on, and then an optional list of test case id's.
Since the labels, values, and id's are in separate lists it can be
difficult to keep track of which fixture corresponds to which value if
you have many of them, and also which group of values corresponds to
which test id. The file structure uses a dict to keep the test id and
the data values together for human readability.

## Features

- Loads data for tests from files
- Multiple test data sets may be in one file
- There may be multiple data files for each test
- Data files may load data from fixtures in other files

## Requirements

This package is a plug-in for `pytest` and works with Python 3.8 and up.
- Tested with `pytest` version 7.4.x, should work with any version
  6.2.5 or higher
- Tested with CPython 3.8 - 3.12 and PyPy 3.9-3.10

## Installation

You can install `pytest-parameterize-from-files` via `pip` from PyPI:

    $ pip install pytest-parameterize-from-files

## Usage

To use this plugin you need to make only two changes to your tests:

1. Create the data file(s) with the proper names and formats
2. Call `pytest` with the flag `--param-from-files`.

You can then access the data from the files via the fixtures defined in
those files. A common use case is to manage multiple test case inputs
and outputs. This allows the developer to change and add test cases
without making changes to the test code.

The unit tests for this package are actually good examples of possible
ways to use this package. Look in the files in the `tests/` directory
and the corresponding files in the `tests/pytester_example_files`
directory.

### Data File Structure

Each data file may contain one or more sets of test data, in either yaml
or json format. The top level is a dict whose keys are the test ids.
Each test id is a dict whose keys are fixture names and whose values are
the test data. An example input file might be:

```yaml
test1:
  input_data_1: 17
  input_data_2: 3
  expected_result: 51

test2:
  input_data_1: 7
  input_data_2: 7
  expected_result: 49
```

This would parameterize into two test cases labeled `test1` and `test2`,
each with three fixtures, `input_data_1`, `input_data_2`, and
`expected_result`.

### File Matching

Data files will be loaded if they match both of the following criteria:

1. They are named for the test function, but swapping the prefix `test_`
   for the prefix `data_` (although the file names may be suffixed by
   any value).
2. They are contained in a folder at or below the file that contains the
   test.

For example, for a test function

    test_foo(...)

the files

    data_foo_part_1.json
    data_foo_part_2.yaml

would both be loaded.

Be careful of tests with names where the name of one is an extended version
of the other. If you have two tests named `test_foo()` and `test_foo_bar()`,
a data file with the name `data_foo_bar.yaml` will be parameterized for
*both* tests. To prevent this, split the two test functions into two separate
files in two different directories or change the name of one of the test
functions.

## Contributing

Since this project is a pytest plug-in, it really does require test-driven
development. If you want to contribute a bug fix or new feature, please
first create a test case that demonstrates what your new code is supposed
to do. Note that you need to set things up using the `pytester` fixture,
rather than testing directly.

This project uses hatch for its environments and build system. You can
run tests using the command `hatch run test`, and `hatch run cov` to
get test coverage.

## License

Distributed under the terms of the `MIT` license,
`pytest-parameterize-from-files` is free and open source software.

## Issues

If you encounter any problems, please `file an issue`_ along with a
detailed description.

## Colophon

Inspired by `pytest-datadir`, `pytest-datafixtures`, and
`pytest-xpara`.
- I wanted to load data from files, but `pytest-datadir` and
  `pytest-datafixtures` required that I read in the file manually.
- I liked the way that `pytest-xpara` loaded data into a fixture,
  but didn't like that it would only work with one file and that
  I had to specify the file on the command line.

This `pytest` plugin was generated with `Cookiecutter` along wit
`@hackebrot`'s `cookiecutter-pytest-plugin`template, then
extensively modified to bring it up to modern standards.

- [Cookiecutter](https://github.com/audreyr/cookiecutter)
- [MIT License](http://opensource.org/licenses/MIT)
- [cookiecutter-pytest-plugin](https://github.com/pytest-dev/cookiecutter-pytest-plugin)
- [file an issue](https://github.com/paulsuh/pytest-parameterize-from-files/issues)
- [pytest](https://github.com/pytest-dev/pytest)
