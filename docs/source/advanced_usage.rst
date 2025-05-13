Advanced Usage
==============

Test Case Merging and Conflicts
-------------------------------

If the same test case id is present in two different files the fixtures from the two
files will be merged as long as a fixture with the same name is not defined more than
once for any particular test case id. For example, for a test function named
``test_foo()`` with two data files:

.. code-block:: yaml
    :caption: ``data_foo_1.yaml``

    test_case_one:
      fixture_one: 17

.. code-block:: yaml
    :caption: ``data_foo_2.yaml``

    test_case_one:
      fixture_two: 170

The function will be passed two fixtures ``fixture_one=17`` and ``fixture_two=170`` for
a test case with ``id=test_case_one``.

*However*, if the fixture names are the same there will be a conflict and the code that
merges the test cases will raise an exception.

Loading Values by Reference
---------------------------

An additional powerful feature is the ability to load the value for a fixture from
another data file. You can have fixture data loaded from another file by setting the
fixture value to a specially formatted string. It must be prefixed with two underscores
and be of the format:

.. code-block::

    fixture_name: __{Filename}:{test case id}:{fixture name}

For instance, a data file ``data_other_check_3.yaml`` might reference the data file
``data_foo_2.yaml`` from the previous section:

.. code-block:: yaml

    check_functionality:
      input_data_1: 42
      other_data: __data_foo_2.yaml:test_case_one:fixture_two

This would result in two fixture values being sent into the test function,
``input_data_1 = 42`` and ``other_data = 170``, for a test case with ``id =
check_functionality``.

.. caution::

    There is nothing preventing an infinite self-referential loop although that is
    something that should be avoided.

Indirect Parameterization
-------------------------

Pytest has a feature called `indirect parameterization`_, where the parameter value is
passed to a fixture function, and the return value of the fixture function is then
passed downstream. You can specify that a fixture should be marked for indirect
parameterization by appending the suffix ``_indirect`` to the fixture name in the data
file. If the data file contains:

.. code-block:: yaml

    test_case_1:
      variable_A: 51
      variable_B_indirect: 3

    test_case_2:
      variable_A: 85
      variable_B_indirect: 5

the corresponding test code would be:

.. code-block:: python

    @pytest.fixture
    def variable_B(request):
        return request.param * 17


    def test_func(variable_A, variable_B):
        assert variable_A == variable_B

The values for fixture ``variable_A`` would be passed directly to ``test_func()``, but
the values for ``variable_B_indirect`` would be passed to the ``variable_B()`` function
and the return value would be passed in as the ``variable_B`` parameter to
``test_func()``.

.. note::

    *Indirect Parameterization and Autouse Fixtures*

    If a fixture is set up for indirect parameterization *and* it is marked as
    ``autouse=True`` then every scenario for every test **must** include a value for
    that fixture, even if it is a null value. The reason is that the fixture will be
    automatically instantiated, and in the process pytest will call the indirect
    function with a fixture ``request`` that should have an attribute ``param`` for the
    input value. If that attribute does not exist, the test will raise an exception
    before the test starts. Alternatively, you can check for the existence of the
    ``request.param`` in the fixture function. If it does not exist, you can then either
    return a default value or handle the missing value some other way.

The psf_expected_result Fixture
-------------------------------

Pytest has a pattern called `Parameterized Conditional Raising`_. This allows the user
to specify either an expected result value **or** an expected Exception that will
be raised. Either way, you can use the same code in the test function and it will
just work. This fixture allows the user to have either an expected exception (including
a match string or regexp) in the scenario file, or any other expected result value.
An exception gets wrapped in a ``pytest.raises()`` context manager, while any other
value gets wrapped in a ``nullcontext()`` context manager. The test function can then
use a call like:

.. code-block:: python

    def test_some_function(psf_expected_result):
        with psf_expected_result as expected_result:
            assert expected_result == some_function()

The scenario should define an indirectly parameterized fixture with the name
``psf_expected_result_indirect``.

- If the value in the data file is a dictionary with the key ``expected_exception_type``,
  the fixture will return a ``pytest.raises()`` context manager with the exception
  pre-loaded. Exceptions that are defined in packages or modules should use their
  full identifier. Any other keys in the dict are passed in to ``pytest.raises()``
  as arguments. In particular, the ``match`` argument is used to match against the
  message of the exception.
- If the value in the data file is a dictionary that does not contain the key
  ``expected_exception_type``, or if the value is not a dictionary, the value will
  be returned wrapped in a ``nullcontext()`` context manager and your test function
  can use it normally.

For a scenario where you expect to get an HTTP 403 error you might set up the expected
result to look for a Requests HTTPError exception:

.. code-block:: yaml

    failure_scenario_1:
        psf_expected_result_indirect:
            expected_exception_type: requests.HTTPError
            match: Authorization failure

On the other hand, for a scenario where you expect a success and want to check
the value returned against a string you set ``psf_expected_result_indirect``
to that string value:

.. code-block:: yaml

    success_scenario_1:
        psf_expected_result_indirect: This is a result string.

This fixture is very useful in conjunction with the Responses and Respx integration.

.. _indirect parameterization: https://docs.pytest.org/en/stable/example/parametrize.html#indirect-parametrization
.. _Parameterized Conditional Raising: https://docs.pytest.org/en/8.3.x/example/parametrize.html#parametrizing-conditional-raising
