APIs
====

There are three APIs that this application uses, each of which has a different
way of retrieving the data.

API 1
-----

This is a straightforward API. It uses a simple HTTPS call, uses OAuth2 service A,
and returns a JSON result.

.. literalinclude:: ../example_files/src/apis.py
    :language: python
    :lines: 9-14

API 2
-----

This API uses OAuth2 service A, but instead of a simple HTTPS call it needs one
call to initiate it and then you need to poll for a response.

.. literalinclude:: ../example_files/src/apis.py
    :language: python
    :lines: 17-35

API 3
-----

This API uses a simple HTTPS call, but it uses OAuth2 service B for access and
returns a text result rather than a JSON result.

.. literalinclude:: ../example_files/src/apis.py
    :language: python
    :lines: 38-
