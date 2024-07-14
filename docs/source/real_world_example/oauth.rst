OAuth2
======

This is using the Hashicorp Vault Lambda Layer, which listens on 127.0.0.1 port
8200. To retrieve a secret we are using IAM authentication; we don't need to pass
anything to the call to the layer, it uses our IAM roles and policies for
authentication and authorization.

There are two Oauth2 services that will return a credentials that are used for
accessing the APIs. Service A is used by two of the APIs, Service B is used
by the third API.

.. include:: ../example_files/src/get_oauth_token.py
    :code: python
    :start-line: 1
