Respx Integration
========================
This library can be used to load http responses from files into the
`Respx`_ package, used for mocking responses with the Httpx package.
This chapter is almost identical to the chapter on Responses
integration. If you are already familiar with the Responses
integration you can just read the Differences below.

.. admonition:: Differences from Responses Integration

    1. Specify the extra ``pytest-scenario-files[respx]`` for installation.
    2. Use the command line flags ``--psf-load-respx``, ``--psf-assert-all-called``,
       and ``--psf-assert-all-mocked`` to load and configure the mocking.
    3. Use the fixture ``psf_respx_mock``.
    4. The keys used by ``respx`` to specify the response are a
       little bit different.

    ========================== ===================
    Responses key              Respx key
    ========================== ===================
    status                     status_code
    body                       text
    content_type function arg  content_type header
    ========================== ===================

    5. Replacing a response in Respx is different from Responses. There
       are no specific methods like ``replace()`` or ``upsert()``. Instead,
       you overwrite an existing response by setting a new response
       route with the same HTTP method and URL.
    6. Responses will automatically queue up successive responses to the
       same method and URL and feed them to the calling test in order.
       Multiple responses for the same method and URL must be specified
       explicitly in Respx.

Basic Usage
-----------

There are three steps to using the Respx integration:

1. Create the data files.
2. Pass the ``psf_respx_mock`` fixture as a parameter to your test
   function.
3. Activate the Respx integration using the command line flags.

Data file format
^^^^^^^^^^^^^^^^
Data to be loaded into responses should be put into fixtures whose names
end with ``_response`` or ``_responses``. For example, you might have a
fixture named ``oauth2_response`` or a fixture named ``api_responses``.
These fixtures will not actually be created or parameterized for the
test. Instead, each will be loaded into the ``psf_respx_mock`` fixture
and removed from the list of fixtures.

Each response should be structured as a dictionary that contains two
required and four optional keys:

.. code-block:: yaml

    scenario_1:
      oauth2_response:
        method: GET|POST|PUT|etc. (required)
        url: https://www.example.com/rest/endpoint (required)
        status_code: 200 (optional)
        text: Text body of the http response (optional)
        json: (optional)
          key1: value1
          key2: value2
          key3: value3
        headers: (optional)
          content_type: text/plain
          header1: header-value-1
          header2: header-value-2

- ``text`` and ``json`` are mutually exclusive and you should only
  use one of the two in a response.
- If you are passing in ``json`` you should not set a ``content-type``
  header as it will be set to ``application/json`` automatically.

The fixture may contain a list of responses in the same format:

.. code-block:: yaml

    scenario_2:
      api_responses:
      - method: GET|POST|PUT|etc.
        url: https://www.example.com/rest/endpoint
        text: Text body of the http response
      - method: GET|POST|PUT|etc.
        url: https://www.example.com/rest/endpoint2
        text: Text body of the http response2
      - method: GET|POST|PUT|etc.
        url: https://www.example.com/rest/endpoint3
        text: Text body of the http response3

All of the responses in the list will be loaded into a MockRouter. While
the response loading recognizes both ``_response`` and ``_responses``,
there is no actual difference in how they are handled. The underlying
code checks to see whether the loaded value is a dict or a list and
handles it accordingly. Having both suffixes is just to make reading
the data files easier for humans.

The ``psf_respx_mock`` fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Pytest-Scenario-Files provides a ``psf_respx_mock`` fixture that is used
to load the responses. It returns a currently active ``respx.MockRouter`` object
that has all of the responses from the data files for the current test
already loaded. If all of the responses your test needs are already loaded
via the data files you can just leave it be. However, If you need to add
additional responses or to change a response for this particular test you
can use it as you would any standard ``MockRouter``.

.. code-block:: Python

    def test_api_call(psf_httpx_mock):
        with httpx.Client() as client:
            http_result = client.get("https://www.example.com/rest/endpoint")
            assert http_result.status_code = 200

Command line flags
^^^^^^^^^^^^^^^^^^
There are three command line flags for Pytest that are used for the
Respx integration:

- ``--psf-load-respx``

  This turns on the integration. Since the fixtures intended for use
  with Respx integration are marked by a special suffix, the
  integration should be explicitly triggered to avoid accidentally
  activating it for a developer who uses the suffix without realizing
  the special meaning.

- ``--psf-assert-all-called=[true|FALSE]``

  This allows you to turn on the flag ``assert_all_called``
  for Respx. It defaults to false.

- ``--psf-assert-all-mocked=[true|FALSE]``

  This allows you to turn on the flag ``assert_all_mocked``
  for Respx. It defaults to false.

Advanced Usage
--------------
Overriding a response
^^^^^^^^^^^^^^^^^^^^^
You can use the ``psf_respx_mock`` fixture to override a response for
a particular test. The replacement can be done in a separate fixture or
in the test function itself. If you are doing this in a separate
fixture the convention is to return the ``MockRouter`` as the fixture
value so that you can chain together multiple fixtures that add or
alter the responses for a test.

.. code-block:: Python

    @pytest.fixture
    def alt_response_mock(psf_respx_mock):
        psf_respx_mock.route(
            method="GET",
            url="https://www.example.com/rest/endpoint3"
        ).respond(status_code=200, text="Alternate response 3.")
        return psf_respx_mock

    def test_endpoint_3_error(alt_response_mock):
        with httpx.Client() as client:
            http_result = client.get("https://www.example.com/rest/endpoint3")
            assert http_result.text == "Alternate response 3."


.. code-block:: yaml
    :caption: ``data_endpoint_3_error.yaml``

    api_call_scenario:
      api_responses:
      - method: GET
        url: https://www.example.com/rest/endpoint
        body: Text body of the http response
      - method: GET
        url: https://www.example.com/rest/endpoint2
        body: Text body of the http response2
      - method: GET
        url: https://www.example.com/rest/endpoint3
        body: Text body of the http response3

Multiple Responses for the Same URL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
There are some test cases where you would want to call the same URL multiple
times. For example, you may need to call a reset endpoint several times as
part of a sequence of tasks; or you may be polling an endpoint to see if a
process has been completed.

- If you put a single response in for a method and URL, Respx will reply
  to repeated requests to that URL with the same response.

- If you want to have different responses to the same method and URL you can
  put the desired responses into a list of responses in the data file, all with
  the same method and URL. Pytest-Scenario-Files will load them into the proper
  place in the MockRouter to respond accordingly. The order of responses is
  guaranteed if they are within the same list of responses, but the order is not
  guaranteed between lists of responses.

Using the following data file will return a status code of 202 and a json block
with ``process_completed = false`` three times, followed by a status code of
200 and a json block with ``process_completed = true``. If the test does a GET
on the URL for a fifth time it will cause a StopIteration exception, as the
list of responses would be exhausted.

.. code-block:: yaml
    :caption: ``data_api_polling_test.yaml``

    api_polling_scenario:
      api_responses:
      - method: GET
        url: https://www.example.com/rest/process_done
        status_code: 202
        json:
          process_completed: false
      - method: GET
        url: https://www.example.com/rest/process_done
        status_code: 202
        json:
          process_completed: false
      - method: GET
        url: https://www.example.com/rest/process_done
        status_code: 202
        json:
          process_completed: false
      - method: GET
        url: https://www.example.com/rest/process_done
        status_code: 200
        json:
          process_completed: true

.. note::

    Pytest-Scenario-Files does not include a way to specify that the last
    response should be repeated forever. The Respx documentation suggests
    that this can be accomplished by using the library functions
    ``itertools.chain()`` and ``itertools.repeat()`` together. When using
    Pytest-Scenario-Files the recommended way to handle this is to create your
    own response override fixture that will set up the proper iteration.

Usage with the ``psf_expected_result`` fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
You can set up a data file with the generally expected response for a specific
URL, then override the response to check error conditions. Here is an example
using a file with the standard API response and a test that checks
both a successful and an unsuccessful test of the API.

This first file contains the basic API responses, which are loaded by
reference for each scenario:

.. code-block:: yaml
    :caption: ``all_api_responses.yaml``

    api_testing:
      api_responses:
      - url: https://www.example.com/rest/endpoint
        method: GET
        status_code: 200
        body: The call was successful.

The second file contains the scenarios, success and failure. The success
scenario just runs through the call and contains no overrides. The failure
scenario specifies that the call should return a 403 error and catch a
``httpx.HTTPError`` exception:

.. code-block:: yaml
    :caption: ``data_api_check_full.yaml``

    success_scenario:
      api_responses: __all_api_responses.yaml:api_testing:api_responses
      psf_expected_result_indirect: The call was successful.
    failure_scenario:
      api_responses: __all_api_responses.yaml:api_testing:api_responses
      response_override_indirect:
        url: https://www.example.com/rest/endpoint
        method: GET
        status_code: 403
        text: Access denied.
      psf_expected_result_indirect:
        expected_exception_type: httpx.HTTPError

The third file is the Python unit tests. It has a fixture ``response_override()``
that will set up an override specified by the scenario. If the scenario
has no override then it will just return the ``psf_respx_mock`` fixture
unchanged.

.. code-block:: Python
    :caption: ``test_api.py``

    @pytest.fixture
    def response_override(request, psf_respx_mock):
        if hasattr(request, "param") and isinstance(request.param, dict):
            response_params = request.param.copy()
            route_match = {k: response_params.pop(k) for k in ("method", "url")}
            respx_mock.route(**route_match).respond(**response_params)
        return psf_respx_mock

    def test_api_check(response_override, psf_expected_result):
        with psf_expected_result as expected_result:
            with httpx.Client() as client:
                http_result = client.get("https://www.example.com/rest/endpoint3")
                api_call_result.raise_for_status()
                assert api_call_result.body == "The call was successful."

When the test is run the first time (``success_scenario``), Respx will
return a 200 response with a body of "The call was successful." — which is
the expected value from the ``psf_expected_result`` fixture.

When the test is run the second time (``failure_scenario``), Respx will
return a 403 response. ``raise_for_status()`` will then raise an exception
``httpx.HTTPError``, which will be caught by the context manager since
the ``psf_expected_value`` fixture will return a ``pytest.raises(httpx.HTTPError)``
context manager object. Any other kind of error or exception will cause the
test to fail.

.. _Respx: https://lundberg.github.io/respx/
