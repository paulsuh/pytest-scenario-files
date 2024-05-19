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

An additional issue with the basic pytest parameterization API is how
the user must provide the parameters. First all of the test case fixture
names in a list, followed by a list of lists with the values the
fixtures will take on, and then an optional list of test case id's.
Since the labels, values, and test case id's are in separate lists it
can be difficult to keep track of which fixture corresponds to which
value if you have many of them, and also which group of values
corresponds to which test id. The file structure uses a dict to keep the
test case id's, fixture names, and data values together in a way that is
easier on the human brain.

### Features

- Loads data for scenarios from files into fixtures
- Multiple scenario data sets may be in one file
- There may be multiple data files for each test
- Fixtures may refer to fixtures in other files
- Can specify indirect parameterization
- Intuitive and sane data file structure

### Compatibility

This package is a plug-in for `pytest` and works with Python 3.9 and up.

- Tested with `pytest` version 7.4.x, should work with any version 6.2.5
  or higher
- Tested with CPython 3.9-3.12 and PyPy 3.9-3.10

While this code currently has a classifier of "Development Status :: 4 -
Beta", it is solid and well-tested. I will likely promote it to
"Development Status :: 5 - Production/Stable" after a little more
real-world usage.

______________________________________________________________________

## Installation

You can install `pytest-scenario-files` from PyPI by using `pip` :

```
$ pip install pytest-scenario-files
```

## Usage

To use this plugin you need to make only two changes to your project:

1. Install the plug-in
2. Create the data file(s) with the proper names and formats

You can then access the data from the files via the fixtures defined in
those files. The most common usage is to manage test case inputs and
expected results. This allows the developer to change and add test cases
without making changes to the test code.

Just as with pytest's basic parameterization, the test function must
have all of the fixtures in its parameter list. Otherwise, an exception
will be raised.

The unit tests for this package are good examples of possible ways to
use this package. Look in the files in the `tests/` directory and the
corresponding files in the `tests/pytester_example_files` directory.

This package is also designed to be transparent for non-parametric
usage. If there are no data files associated with a particular test the
fixtures will not be parameterized and everything will work as though
the plug-in was not present.

### Data File Matching

A data file will be loaded if it matches all of the following criteria:

1. The filename starts with `data_`, followed by the name of the test
   function with the prefix `test_` removed. The remainder of the
   filename may be any value, and is usually used to identify the tests
   contained in the file.
2. The filename must end in `.json`, `.yaml`, or `.yml`.
3. The file is contained in a folder at or below the file that contains
   the test.

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

*Caution*: Beware of situations where the name of one test is an
extended version of another. E.g., if you have two tests named
`test_foo()` and `test_foo_bar()`, a data file with the name
`data_foo_bar.yaml` will be loaded for *both* tests. To prevent this,
split the two test functions into two separate files in two different
directories or change the name of one of the test functions. See
`test_load_file_extended_name.py` and `test_load_separate_subdirs.py` in
the unit test files for this package for concrete examples of what might
happen and how to avoid it.

### Data File Structure

Each data file may contain one or more sets of test data, in either yaml
or json format. The top level is a dict whose keys are the test id's.
Each test id is a dict whose keys are fixture names and whose values are
the test data. The test data may be anything, including container types
such as lists or dicts. An example input file `data_foo_bar.yaml` might
contain:

```yaml
test1:
  input_data_1: 17
  input_data_2: 3
  expected_result: 51

test2:
  input_data_1:
    - abc
  input_data_2: 3
  expected_result:
    - abc
    - abc
    - abc
```

This would parameterize into two test cases labeled `test1` and `test2`,
each with three fixtures, `input_data_1`, `input_data_2`, and
`expected_result`.

### Test Case Merging and Conflicts

If the same test case id is present in two different files, the fixtures
from the two files will be merged as long as a fixture with the same
name is not defined more than once for any particular test case id. For
example, for a test function named `test_foo()` with two data files:

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

### Loading Fixture Values by Reference

An additional powerful feature is the ability to load the value for a
fixture from another data file. You can have fixture data loaded from
another file by setting the fixture value to a specially formatted
string. It must be prefixed with two underscores and be of the format:

```
__<Filename>:<test case id>:<fixture name>
```

For instance, a data file `data_other_check_3.yaml` might reference the
data file `data_foo_2.yaml` from the previous section:

```yaml
check_functionality:
  input_data_1: 42
  other_data: __data_foo_2.yaml:test_case_one:fixture_two
```

This would result in two fixture values being sent into the test
function, `input_data_1 = 42` and `other_data = 170`, for a test case
with `id = check_functionality`. (Note that there is nothing preventing
an infinite self-referential loop although that is something that should
be avoided).

### Indirect Parameterization

Pytest has a feature called [indirect parameterization][link08], where
the parameter value is passed to a fixture function, and the return
value of the fixture function is then passed downstream. You can specify
that a fixture should be marked for indirect parameterization by
appending the suffix `_indirect` to the fixture name in the data file.
If the data file contains:

```yaml
test_case_1:
  variable_A: 51
  variable_B_indirect: 3

test_case_2:
  variable_A: 85
  variable_B_indirect: 5
```

the corresponding test code would be:

```python
@pytest.fixture
def variable_B(request):
    return request.param * 17


def test_func(variable_A, variable_B):
    assert variable_A == variable_B
```

The values for fixture `variable_A` would be passed directly to
`test_func()`, but the values for `variable_B_indirect` would be passed
to the `variable_B()` function and the return value would be passed in
as the `variable_B` parameter to `test_func()`.

______________________________________________________________________

## Reporting Issues

If you encounter any problems, please [file an issue][link09] including
a detailed description and (if possible) an example of the problem.

## Contributing

Since this project is a pytest plug-in, it really does require
test-driven development. If you want to contribute a bug fix or new
feature, please first create a test case that demonstrates what your new
code is supposed to do. Note that you need to set things up using the
`pytester` fixture, rather than testing directly.

This project uses [hatch][link10] for its environments and build system,
as well as [pre-commit][link11], [ruff][link12], and [mdformat][link13]
for formatting and linting. Before you send in a pull request, please:

- Set up `pre-commit` and use it to run `ruff` and `mdformat` with the
  settings included in the `pyproject.toml` and
  `.pre-commit-config.yaml` files
- Run tests using the command `hatch run test:test`, which will run all
  of the tests against CPython 3.9-3.12 and PyPy 3.9-3.10
- Check test coverage with `hatch run cov`

## License

Distributed under the terms of the `MIT` license,
`pytest-scenario-files` is free and open source software.

## Colophon

This plug-in was originally named `pytest-parameterize-from-files`. It
was inspired by the pytest plug-ins `pytest-datadir`,
`pytest-datafixtures`, and `pytest-xpara`. I also later found the
non-plug-in package `parameterize-from-file`. To avoid confusion and
provide a more descriptive title, I renamed this project to
`pytest-scenario-files`.

- I wanted to load data from files without having to write any
  additional code. However, `pytest-datadir` and `pytest-datafixtures`
  required code in the test or fixtures specifically to read in the
  file.
- I liked the way that `pytest-xpara` loaded data into a fixture, but
  didn't like that it would only work with one file and that I had to
  specify the file on the command line.
- After I wrote much of this project I found the package
  `parameterize-from-files` which has a similar name. It's a powerful
  and capable tool, but it's not to my taste as I think it's trying too
  hard.
  - It requires a decorator per test function, with potentially complex
    syntax inside the decorator's arguments.
  - It lets the user place code snippets into the data files which will
    be a maintenance problem down the road. It's cleaner to take
    advantage of Pytest's indirect parameterization feature instead.
  - Having to import the package in every test file and decorate each
    function increases the complexity of the test code.

In general I wanted the data file handling to be scalable:

- If you have 50 unit tests you don't have to specify all 50 files to
  load in code or on the command line.
- You can reference data from other files to keep duplication low.

This `pytest` plugin was developed using a skeleton generated by
[`cookiecutter`][link14] along with the
[`cookiecutter-pytest-plugin`][link15] template, then extensively
modified to bring it up to modern standards.

______________________________________________________________________

[link01]: https://img.shields.io/pypi/pyversions/pytest-parameterize-from-files.svg
[link02]: https://img.shields.io/badge/Pytest-Plug--in-orange?logo=pytest
[link03]: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
[link04]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[link05]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
[link06]: https://github.com/paulsuh/pytest-scenario-files
[link07]: https://docs.pytest.org/en/stable/index.html
[link08]: https://docs.pytest.org/en/stable/example/parametrize.html#indirect-parametrization
[link09]: https://github.com/paulsuh/pytest-scenario-files/issues
[link10]: https://github.com/pypa/hatch
[link11]: https://pre-commit.com
[link12]: https://github.com/astral-sh/ruff
[link13]: https://github.com/executablebooks/mdformat
[link14]: https://pypi.org/project/cookiecutter/
[link15]: https://github.com/pytest-dev/cookiecutter-pytest-plugin
