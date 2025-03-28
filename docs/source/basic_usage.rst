Basic Usage
===========

There are two parts to using ``pytest-scenario-files``.

1. Decide on the fixtures that will be changed in each scenario.
2. Create the data files.

Each fixture must be present in the argument list of the test function. For example, a
target function and a corresponding test function might be:

.. code-block:: python
    :caption: target function

    def foo(x, y):
        return x * y

.. code-block:: python
    :caption: test function

    def test_foo(input_data_1, input_data_2, expected_result):
        assert expected_result == foo(input_data_1, input_data_2)

The test function expects there to be three fixtures which may be defined as regular
``pytest`` fixtures or via a data file.

Data File Structure
-------------------

Each data file may contain one or more sets of test data, in either yaml or json format.
The top level is a dict whose keys are the test id’s. Each test id is a dict whose keys
are fixture names and whose values are the test data. The test data may be anything,
including container types such as lists or dicts. An example data file might contain:

.. code-block:: yaml
    :caption: data_foo_1.yaml

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

This would parameterize into two test cases labeled ``test1`` and ``test2``, each with
three fixtures, ``input_data_1``, ``input_data_2``, and ``expected_result``.

Because of the nature of parameterization, *every scenario* **must** *have the same set of
fixtures*, even if the fixture is unused in some circumstances. You can put in an empty
string or null value if necessary.

Integrating With Regular Fixtures
---------------------------------

If you want to use a standard fixture along side the scenarios, don't define a fixture
value in the data file. Instead, create a fixture in your test file or ``conftest.py``.

For the example target and test functions above, you could define a regular fixture
``input_data_2()``, removing the ``input_data_2`` key from the data file:

.. code-block:: python
    :caption: conftest.py

    @pytest.fixture
    def input_data_2():
        return 5

.. code-block:: yaml
    :caption: data_foo_1.yaml

    test1:
      input_data_1: 17
      expected_result: 85

    test2:
      input_data_1:
        - abc
      expected_result:
        - abc
        - abc
        - abc
        - abc
        - abc

Data File Matching and Loading
------------------------------

Data files must have a filename extension of ``.json``, ``.yaml``, or ``.yml``. They are
matched to tests based on the name of the test. A data file will be loaded if it matches
all of the following criteria:

1. The filename starts with ``data_``, followed by the name of the test function with
   the prefix ``test_`` removed. The remainder of the filename may be any value, and is
   usually used to identify the tests contained in the file.
2. The filename ends in ``.json``, ``.yaml``, or ``.yml``.
3. The file is contained in a folder at or below the file that contains the test.

For example, for the target function ``foo()`` and test function ``test_foo()`` above,
the files

.. code-block::

    data_foo_part_1.json
    data_foo_part_2.yaml
    subfolder/data_foo.yaml

would all be loaded.

.. caution::

    *Test and Data File Name Conflicts*

    Beware of situations where the name of one test is an extended version of another.
    E.g., if you have two tests named ``test_foo()`` and ``test_foo_bar()``, a data file
    with the name ``data_foo_bar.yaml`` will be loaded for *both* tests. To prevent
    this, split the two test functions into two separate files in two different
    directories or change the name of one of the test functions. See
    ``test_load_file_extended_name.py`` and ``test_load_separate_subdirs.py`` in the
    unit test files for this package for concrete examples of what might happen and how
    to avoid it.
