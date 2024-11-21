Responses Integration
=====================
This library can be used to load http responses from files into the
`Responses`_ package. While Responses has a native file loading capability
in beta, Pytest-Scenario-Files can also load the responses from its
own files.

Basic Usage
-----------

There are three steps to using the Responses integration:

1. Create the data files.
2. Pass the ``psf-responses`` fixture as a parameter to your test
   function.
3. Activate the Responses integration using the command line flags.

Data file format
^^^^^^^^^^^^^^^^
Data to be loaded into responses should be put into fixtures whose names
end with ``_response`` or ``_responses``. For example, you might have a
fixture named ``oauth2_response`` or a fixture named ``api_responses``.
These fixtures will not actually be created or parameterized for the
test. Instead, each will be loaded into the ``psf-responses`` fixture
and removed from the list of fixtures.

Each response should be structured as a dictionary that contains two
required and five optional keys:

.. code-block:: yaml

    scenario_1:
      oauth2_response:
        method: GET|POST|PUT|etc. (required)
        url: https://www.example.com/rest/endpoint (required)
        status: 200 (optional)
        body: Text body of the http response (optional)
        json: (optional)
          key1: value1
          key2: value2
          key3: value3
        content_type: text/plain (optional)
        headers: (optional)
          header1: header-value-1
          header2: header-value-2

- ``body`` and ``json`` are mutually exclusive and you should only
  use one of the two in a response.
- If you are passing in ``json`` you should not pass in a ``content_type``
  header as it should be set to ``application/json`` automatically.

The fixture may contain a list of responses in the same format:

.. code-block:: yaml

    scenario_2:
      api_responses:
      - method: GET|POST|PUT|etc.
        url: https://www.example.com/rest/endpoint
        body: Text body of the http response
      - method: GET|POST|PUT|etc.
        url: https://www.example.com/rest/endpoint2
        body: Text body of the http response2
      - method: GET|POST|PUT|etc.
        url: https://www.example.com/rest/endpoint3
        body: Text body of the http response3

All of the responses in the list will be loaded into the RequestsMock
for the fixture ``psf-responses``. While the response loading recognizes
both ``_response`` and ``_responses``, there is no actual difference
in how they are handled. They underlying code checks to see whether
the loaded value is a dict or a list and handles it accordingly.
Having both suffixes is just to make reading the data files easier
for humans.

- Loading values by reference will work as expected. See the detailed
  example for how it is used.
- Support for loading native Responses files is planned for the near
  future.
- Support for additional responses features like various matchers for
  headers, query parameters, json body, etc. is under consideration.
- Support for ``httpx`` and ``httpx-responses`` is also planned for
  the future.

The ``psf-responses`` fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Pytest-Scenario-Files provides a ``psf-responses`` fixture that is used
to load the responses. It returns a currently active RequestsMock object
that has all of the responses from the data files for the current test
already loaded. If all of the responses your test needs are already loaded
via the data files you can just leave it be. However, If you need to add
additional responses or to change a response for this particular test you
can use it as you would any standard RequestsMock.

.. code-block:: Python

    def test_api_call(psf_responses):
        http_result = requests.get("https://www.example.com/rest/endpoint")
        assert http_result.status_code = 200

Command line flags
^^^^^^^^^^^^^^^^^^
There are two command line flags for Pytest that are used for the
Responses integration:

- ``--psf-load-responses``

  This turns on the integration. Since the fixtures intended for use
  with Responses integration are marked by a special suffix, the
  integration should be explicitly triggered to avoid accidentally
  activating it for a developer who uses the suffix without realizing
  the special meaning.

- ``--psf-fire-all-responses=[true|false]``

  This allows you to turn on the flag ``assert_all_requests_are_fired``
  for Responses. It defaults to false.

Advanced Usage
--------------
Overriding a response
^^^^^^^^^^^^^^^^^^^^^
You can use the ``psf-responses`` fixture to override a response for
a particular test. Use the ``replace()`` or ``upsert()`` methods
to do this. The replacement can be done in a separate fixture or
in the test function itself. If you are doing this in a separate
fixture the convention is to return the RequestsMock as the fixture
value so that you can chain together multiple fixtures that add or
alter the responses for a test.

.. code-block:: Python

    @pytest.fixture
    def error_response(psf_responses):
        psf_responses.replace(
            "GET",
            "https://www.example.com/rest/endpoint3",
            status=401
        )
        return psf_responses

    def test_endpoint_3_error(error_response):
        http_result = requests.get("https://www.example.com/rest/endpoint3")
        assert http_result.status_code = 401


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

Use with ``moto`` when mocking AWS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
If you are using the package `moto`_ to mock out AWS services, note
that it uses Responses under the hood and sets its own RequestsMock.
This will cause your own responses to not be found. You will need to
call ``override_responses_real_send()`` as per the `moto FAQ`_.

.. code-block:: Python

    from moto.core.models import override_responses_real_send

    def test_some_func(psf_responses):
        override_responses_real_send(psf_responses)
        ...

Detailed Example
----------------
The easiest way to see how this works is to take an example. One system
I work with (the `NetBrain API`_) requires that you make four calls when
you connect to it.

1. Authenticate and get an access token.
2. Get the list of available tenants and their tenant IDs.
3. Get the list of available domains and their domain IDs for the
   specified tenant.
4. Set the tenant and domain to be used for the current session.

In addition to checking for an HTTP error code of 4xx or 5xx, you also
need to check the status code in the response JSON. 790200 generally
means the API call succeeded while anything else means it failed.

The complete example (with the API connection code, test code,
and data files) is contained in the source repository in the
`tests/Responses_example`_ directory. Some highlights of this
example are:

1. The ``common_test_data.yaml`` file. This holds a common set of responses
   that are used as a base by all of the tests.

.. code-block:: yaml

    common_scenario_data:
      common_responses:
        - method: POST
          url: https://netbrain-api.example.com/ServicesAPI/API/V1/Session
          status: 200
          json:
            statusCode: "790200"
            token: mock_token
        - method: GET
          url: https://netbrain-api.example.com/ServicesAPI/API/V1/CMDB/Tenants
          status: 200
          json:

2. Multiple scenarios (both success and failure) in each data file, covering
   both the happy (successful) path and any error paths through the code.

3. Each failure scenario uses a custom fixture ``url_response_override``
   along with data from the file to give an error response.

.. code-block:: yaml

    url_response_override_indirect:
      method_or_response: GET
      url: https://netbrain-api.example.com/ServicesAPI/API/V1/CMDB/Domains
      status: 403
      json:
        statusCode: "795000"

4. Each failure scenario uses the ``psf_expected_result`` fixture with
   a dict containing a item with the key ``expected_exception_name``
   to indicate the expected failure mode.

.. code-block:: yaml

    psf_expected_result_indirect:
      expected_exception_name: requests.HTTPError

5. Use of a regular, un-parameterized fixture that is used to prepare
   a NetbrainConnection object for each test.

.. code-block:: Python

    @pytest.fixture
    def netbrain_connection_obj() -> NetBrainConnection:
        return NetBrainConnection("username", "mock_password",
            "mock_tenant_name", "mock_domain_name")

Running all of the tests will give you complete coverage for the
``api_connection.py`` file.

.. _Responses: https://github.com/getsentry/responses
.. _moto: https://github.com/getmoto/moto
.. _moto FAQ: http://docs.getmoto.org/en/stable/docs/faq.html#how-can-i-mock-my-own-http-requests-using-the-responses-module
.. _Netbrain API: https://github.com/NetBrainAPI/NetBrain-REST-API-R11.1/blob/main/REST%20APIs%20Documentation/Authentication%20and%20Authorization/Login%20API.md
.. _tests/Responses_example: https://github.com/paulsuh/pytest-scenario-files/tree/main/tests/Responses_example
