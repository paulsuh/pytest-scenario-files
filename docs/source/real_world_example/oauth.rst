OAuth2
======

Retrieving an Auth Secret
-------------------------

This is using the Hashicorp Vault Lambda Layer, which listens on 127.0.0.1 port
8200. To retrieve a secret we are using IAM authentication; we don't need to pass
anything to the call to the layer, it uses our IAM roles and policies for
authentication and authorization.

.. literalinclude:: ../example_files/src/get_oauth_token.py
    :language: python
    :lines: 6-9

Getting the OAuth2 Token
------------------------

There are two Oauth2 services that will return a credentials that are used for
accessing the APIs. Service A is used by two of the APIs, Service B is used
by the third API.

.. literalinclude:: ../example_files/src/get_oauth_token.py
    :language: python
    :lines: 12-35
