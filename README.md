# pytest-parameterize-from-files

![PyPI pyversions][pypi versions] ![Pytest][pytest shield]

![PyPaHatch][pypa hatch shield] ![Ruff Formatter][ruff formatter shield]
![Ruff Linter][ruff linter shield] ![Pre-Commit][pre-commit shield]

A [`pytest-parameterize-from-files`][project home] is a
[`pytest`][pytest docs] plugin that parameterizes tests using data
loaded from data files using the hook
[`pytest_generate_tests()`][pytest generate tests].

______________________________________________________________________

## Making Test Parameterization Easy and Scalable

`pytest` has a feature called parameterization that allows you to run
the same test function repeatedly using different inputs to test
multiple cases. However, managing the test data for parameterization can
be a problem. Sometimes the input data is very large or there are many
test cases, so that it is impractical to put all of the data into the
source code of the test.

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

### Features

- Loads data for tests from files
- Multiple test data sets may be in one file
- There may be multiple data files for each test
- Data files may load data from fixtures in other files
- Intuitive and sane data file structure

### Compatibility

This package is a plug-in for `pytest` and works with Python 3.9 and up.

- Tested with `pytest` version 7.4.x, should work with any version 6.2.5
  or higher
- Tested with CPython 3.9-3.12 and PyPy 3.9-3.10

______________________________________________________________________

## Installation

You can install `pytest-parameterize-from-files` via `pip` from PyPI:

```
$ pip install pytest-parameterize-from-files
```

## Usage

To use this plugin you need to make only two changes to your tests:

1. Create the data file(s) with the proper names and formats
2. Call `pytest` with the flag `--param-from-files`

An example command line would be:

```
$ pytest --param-from-files
```

You can then access the data from the files via the fixtures defined in
those files. A common use case is to manage test case inputs and
expected results. This allows the developer to change and add test cases
without making changes to the test code.

Just as with pytest's basic parameterization, the test function must
have all of the fixtures in its parameter list. Otherwise, an exception
will be raised.

The unit tests for this package are good examples of possible ways to
use this package. Look in the files in the `tests/` directory and the
corresponding files in the `tests/pytester_example_files` directory.

### Data File Matching

Data files will be loaded if they match both of the following criteria:

1. They are named for the test function, but swapping the prefix `test_`
   for the prefix `data_` (although the file names may be suffixed by
   any value).
2. They are contained in a folder at or below the file that contains the
   test.

For example, for a test function

```
test_foo(...)
```

the files

```
data_foo_part_1.json
data_foo_part_2.yaml
subfolder/data_foo.yaml
```

would all be loaded.

Be careful of tests with names where the name of one is an extended
version of the other. If you have two tests named `test_foo()` and
`test_foo_bar()`, a data file with the name `data_foo_bar.yaml` will be
parameterized for *both* tests. To prevent this, split the two test
functions into two separate files in two different directories or change
the name of one of the test functions. See
`test_load_file_extended_name.py` and `test_load_separate_subdirs.py` in
the unit test files for this package for concrete examples of what might
happen and how to avoid it.

### Data File Structure

Each data file may contain one or more sets of test data, in either yaml
or json format. The top level is a dict whose keys are the test ids.
Each test id is a dict whose keys are fixture names and whose values are
the test data. An example input file `data_foo_bar.yaml` might contain:

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

### Test Case Merging and Conflicts

If the same test case id is present in two different files, the fixtures
from the two files will be merged as long as a fixture with the same
name is not defined more than once for any particular test case id. For
example, for a test function named `test_foo()` with the two data files:

File `data_foo_1.yaml`;

```yaml
test_case_one:
  fixture_one: 17
```

File `data_foo_2.yaml`;

```yaml
test_case_one:
  fixture_two: 170
```

The function will be passed two fixtures `fixture_one=17` and
`fixture_two=170` for a test case with `id=test_case_one`.

*However*, if the fixture names are the same there will be a conflict
and the code that merges the test cases will raise an exception.

### Loading Fixtures by Reference

An additional powerful feature is the ability to load a data for a
fixture from another data file. You can have fixture data loaded from
another file by setting the fixture value to a special string value. It
must be prefixed with two underscores and be of the format:

```
__<Filename including extension>:<test name>:<fixture name>
```

For instance a data file `data_other_check_3.yaml` might reference a
data file from the previous section:

```yaml
check_functionality:
  input_data_1: 42
  other_data: __data_foo_bar.yaml:test2:input_data_1
```

This would result in two fixture values being sent into the test
function, `input_data_1 = 42` and `other_data = 7`, for a test case with
`id = check_functionality`. Note that there is nothing preventing an
infinite self-referential loop (although that is something that should
be avoided).

______________________________________________________________________

## Reporting Issues

If you encounter any problems, please [file an issue][project issues]
including a detailed description and (if possible) an example of the
problem.

## Contributing

Since this project is a pytest plug-in, it really does require
test-driven development. If you want to contribute a bug fix or new
feature, please first create a test case that demonstrates what your new
code is supposed to do. Note that you need to set things up using the
`pytester` fixture, rather than testing directly.

This project uses [hatch][hatch home] for its environments and build
system, as well as [pre-commit][pre-commit home] and [ruff][ruff home]
for formatting and linting. Before you send in a pull request, please:

- Run `ruff` with the settings in the `pyproject.toml` file
- Run tests using the command `hatch run test:test`, which will run all
  of the tests against CPython 3.9-3.12 and PyPy 3.9-3.10
- Check test coverage with `hatch run cov`

## License

Distributed under the terms of the `MIT` license,
`pytest-parameterize-from-files` is free and open source software.

## Colophon

Inspired by the pytest plug-ins `pytest-datadir`, `pytest-datafixtures`,
and `pytest-xpara`.

- I wanted to load data from files, but `pytest-datadir` and
  `pytest-datafixtures` required that I read in the file manually.
- I liked the way that `pytest-xpara` loaded data into a fixture, but
  didn't like that it would only work with one file and that I had to
  specify the file on the command line.

This `pytest` plugin was developed using a skeleton generated by
[`cookiecutter`][cookiecutter home] along with the
[`cookiecutter-pytest-plugin`][cookiecutter-pytest-plugin home]
template, then extensively modified to bring it up to modern standards.

______________________________________________________________________

[cookiecutter home]: https://pypi.org/project/cookiecutter/
[cookiecutter-pytest-plugin home]: https://github.com/pytest-dev/cookiecutter-pytest-plugin
[hatch home]: https://github.com/pypa/hatch
[pre-commit home]: https://pre-commit.com
[pre-commit shield]: https://img.shields.io/badge/Pre--Commit-passed-green?logo=precommit
[project home]: https://github.com/paulsuh/pytest-parameterize-from-files
[project issues]: https://github.com/paulsuh/pytest-parameterize-from-files/issues
[pypa hatch shield]: https://img.shields.io/badge/PyPa-Hatch-green
[pypi versions]: https://img.shields.io/pypi/pyversions/pytest-parameterize-from-files.svg
[pytest docs]: https://docs.pytest.org/en/stable/index.html
[pytest generate tests]: https://docs.pytest.org/en/stable/reference/reference.html#collection-hooks
[pytest shield]: https://img.shields.io/badge/Pytest-Plug--in-orange?logo=pytest
[ruff formatter shield]: https://img.shields.io/badge/Ruff-Formatter-green
[ruff home]: https://github.com/astral-sh/ruff
[ruff linter shield]: https://img.shields.io/badge/Ruff-Linter-green
