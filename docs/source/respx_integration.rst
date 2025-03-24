Respx Integration
========================
This library can be used to load http responses from files into the
`Respx`_ package, used for mocking responses with the httpx package.
This chapter is almost identical to the chapter on Responses
integration. If you are already familiar with the Responses
integration you can just read the TL; DR.

TL; DR
------
The differences are:

1. Specify the extra ``pytest-scenario-files[respx]`` for installation.
2. Use the command line flag ``--psf-load-respx``.
3. Use the fixture ``psf_respx_mock``.
4. The keys used by ``respx`` to specify the response are a
   little bit different.

========================== ===================
Responses key              respx key
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
   same method and URL and feed them to the calling test automatically.
   Multiple responses for the same method and URL must be done explicitly
   in Respx and is not yet supported in Pytest-Scenario-Files.

Basic Usage
-----------

There are three steps to using the Responses integration:

1. Create the data files.
2. Pass the ``psf_respx_mock`` fixture as a parameter to your test
   function.
3. Activate the respx integration using the command line flags.

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

All of the responses in the list will be loaded into the HTTPXMocker
for the fixture ``psf_httpx_mock``. While the response loading recognizes
both ``_response`` and ``_responses``, there is no actual difference
in how they are handled. They underlying code checks to see whether
the loaded value is a dict or a list and handles it accordingly.
Having both suffixes is just to make reading the data files easier
for humans.

.. note::

    Loading values by reference will work as expected. See the detailed
    example for how it is used.

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
There are two command line flags for Pytest that are used for the
Responses integration:

- ``--psf-load-respx``

  This turns on the integration. Since the fixtures intended for use
  with Respx integration are marked by a special suffix, the
  integration should be explicitly triggered to avoid accidentally
  activating it for a developer who uses the suffix without realizing
  the special meaning.

- ``--psf-fire-all-responses=[true|false]``

  This allows you to turn on the flag ``assert_all_requests_are_fired``
  for Respx. It defaults to false.

Advanced Usage
--------------
Overriding a response
^^^^^^^^^^^^^^^^^^^^^
You can use the ``psf_respx_mock`` fixture to override a response for
a particular test. The replacement can be done in a separate fixture or
in the test function itself. If you are doing this in a separate
fixture the convention is to return the RequestsMock as the fixture
value so that you can chain together multiple fixtures that add or
alter the responses for a test.

.. code-block:: Python

    @pytest.fixture
    def error_response(psf_respx_mock):
        psf_respx_mock.route(
            method="GET",
            url="https://www.example.com/rest/endpoint3"
        ).respond(status_code=404, text="Not found.")
        return psf_respx_mock

    def test_endpoint_3_error(error_response):
        http_result = requests.get("https://www.example.com/rest/endpoint3")
        assert http_result.status_code = 404


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

This is intended to be used with the ``psf_expected_result`` fixture
and an indirectly parameterized override for error scenarios. See the
data files that go with the detailed example section to see how it
all works together.

.. _Respx: https://lundberg.github.io/respx/
.. _moto: https://github.com/getmoto/moto
.. _moto FAQ: http://docs.getmoto.org/en/stable/docs/faq.html#how-can-i-mock-my-own-http-requests-using-the-responses-module
.. _Netbrain API: https://github.com/NetBrainAPI/NetBrain-REST-API-R11.1/blob/main/REST%20APIs%20Documentation/Authentication%20and%20Authorization/Login%20API.md
.. _tests/Responses_example: https://github.com/paulsuh/pytest-scenario-files/tree/main/tests/Responses_example
