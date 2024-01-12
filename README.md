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

This `pytest` plugin was generated with `Cookiecutter` along with `@hackebrot`'s `cookiecutter-pytest-plugin` template.


## Features

* TODO


## Requirements

* TODO


## Installation

You can install "pytest-parameterize-from-files" via `pip`_ from `PyPI`_::

    $ pip install pytest-parameterize-from-files

## Usage

To use this plugin you need to make only two changes to your test code:
1. Create the data file(s) with the proper names and formats
2. Add the fixture `paramfiledata` to your test function

You can then access the data from the files via the `paramfiledata` fixture. 
A common use case is to manage multiple test case inputs and outputs. This allows
the developer to change and add test cases without making changes to the test code. 

## Data File Structure
Each data file may contain one or more sets of test data. This plugin supports
yaml, json, and toml files. The top level is a dict that contains a key with
the test id, followed by a data structure that contains the test data. The 
actual content of the test data is left up to the developer, but a suggested
convention is that it consists of a dict with two keys, `input` and 
`result`. An example input file might be: 

```yaml
test1:
  input: 
    x: 17
    y: 3
  result: 51

test2: 
  input:
    x: 7
    y: 7
  result: 49
```

This would parameterize into two test cases labeled `test1` and `test2`. 

## File Matching
Data files will be loaded if they match both of the following criteria: 
1. They are named for the test with or without the `test_` prefix (although they 
may be suffixed by any value). 
2. They are contained in a folder at or below the file that contains the test. 

Be careful of tests with extended names. If you have two tests, `test_foo()` and 
`test_foo_bar()` in the same file, a data file with the name `test_foo_bar.yaml` 
will be parameterized for *both* tests. To prevent this, split the two test 
functions into two separate files in two different directories. 

## Contributing
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the `MIT` license, "pytest-parameterize-from-files" is free and open source software


## Issues

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/paulsuh/pytest-parameterize-from-files/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
