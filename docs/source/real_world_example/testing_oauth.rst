Testing the OAuth2 Calls
========================

There are two levels to testing the OAuth2 calls, retrieving the secret and
then getting the authentication token. We need to check both.

Test Secret Retrieval
---------------------

There are three parts to this test, beyond the target function ``_retrieve_secret()``.

1. The test function ``test_retrieve_secret(client_secret_responses, client_id, expected_secret)``,
   which takes three fixtures. Two are straightforward, ``client_id`` and ``expected_secret``.
   The normal parameterization process will handle them. The ``client_secret_responses``
   fixture, on the other hand, requires an indirect parameterization to set up the
   ``Responses`` library.

.. literalinclude:: ../example_files/tests/unit_tests/test_oauth.py
    :language: python
    :lines: 9-14

2. The data file, in this case ``data_retrieve_secret.yaml``. This contains four
   scenarios which will be used to test both sources A and B as well as success
   and failure. This is an example of a success scenario and a failure scenario.
   Note the HTTP status code of 200 and the ``expected_secret`` value of
   ``mockClientSecretA`` for the success and the HTTP status code of 404 and
   the ``expected_secret`` value of ``null`` for the failure. Also note that the
   name of the fixture in the data file is ``client_secret_responses_indirect``,
   which flags it for the plug-in so that it will mark the fixture
   ``client_secret_responses`` for indirect parameterization.

.. literalinclude:: ../example_files/tests/unit_tests/test_data/data_retrieve_secret.yaml
    :language: yaml
    :lines: 1-19
    :emphasize-lines: 2,5,13,16

3. The ``conftest.py`` file, which handles the indirect parameterization of the
   ``client_secret_responses`` fixture. This is where (some) of the magic happens.
   The responses are set up by reading from the data file and putting them into
   a ``ResponsesMock`` object that is ``yield``-ed to the caller.

.. literalinclude:: ../example_files/tests/unit_tests/conftest.py
    :language: python
    :lines: 7-19

The test execution process is:

1. Pytest generates four scenarios and sets up the three fixtures for each one.
2. Each scenario is run and the a request is made to ``https://127.0.0.1:8200/v1/{lockbox_id}/{secret_id}``
   which is then mocked out by the Responses library.
3. Depending on the scenario, either a mock client secret is returned or an
   ``HTTPError`` is raised.

Test Getting the OAuth2 Tokens
------------------------------

This uses a similar structure as the test for retrieving secrets, but it also
shows how to load test data by reference. It also shows how we can build on the
responses used from the previous tests.

1. The test function is similar to the previous one, but it needs to check both
   success and failure for services A and B. There might be a cleaner way to write
   this test function, but this will do for an example. The fixtures it uses are
   ``auth_tokens_responses``, ``client_id``, and ``expected_oauth_token``.

.. literalinclude:: ../example_files/tests/unit_tests/test_oauth.py
    :language: python
    :lines: 17-29

2. The data file's name needs to match the function, so it is ``data_get_oauth_token.yaml``.
   Here are two example cases, one success and one failure. Note there are two
   indirectly parameterized fixtures: ``auth_tokens_responses_indirect`` and
   ``client_secret_responses_indirect``. The second fixture is pulling in its data by
   reference from ``data_retrieve_secret.yaml``, since the value is prefixed by
   a double underscore.

.. literalinclude:: ../example_files/tests/unit_tests/test_data/data_get_oauth_token.yaml
    :language: yaml
    :lines: 1-28
    :emphasize-lines: 13, 27

3. The indirect parameterization function in the ``conftest.py`` file is similar
   to the first, but it uses the fixture ``client_secret_responses`` as well as
   the ``request`` fixture. This lets us build on the responses from the first
   test. The ``client_secret_responses`` fixture comes in as a ``RequestsMock``
   object, and we can add on additional responses.

.. literalinclude:: ../example_files/tests/unit_tests/conftest.py
    :language: python
    :lines: 22-31
