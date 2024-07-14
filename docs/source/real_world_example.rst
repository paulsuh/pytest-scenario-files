A Real World Example
====================

This is a slightly simplified and anonymized real world example of how you
might use this plug-in.

Our application calls multiple APIs, each of which uses OAuth2 for authentication
and authorization. However, while some of share an authentication URL and
service account credentials, others use a different URL and credentials. To
get the service account credentials, we need to make a call into a lambda layer
that communicates on 127.0.0.1:8200 using http (not https!).

We want to test successful and unsuccessful cases of each API call, and for a
variety of reasons. There are many URLs to keep track of and parameterize
into a prethora of scenarios. Trying to do this using standard pytest
parameterization is would be a lot of work.

The Example Code
================

All of these files are available in the repository in the XXXXXX folder.

OAuth2
------

This is using the Hashicorp Vault Lambda Layer, which listens on 127.0.0.1 port
8200. To retrieve a secret we are using IAM authentication; we don't need to pass
anything to the call to the layer, it uses our IAM roles and policies for
authentication and authorization.

There are two Oauth2 services that will return a credentials that are used for
accessing the APIs. Service A is used by three of the APIs, Service B is used
by the fourth API

.. include:: example_files/src/get_oauth_token.py
    :code: python


API 1
-----

This is the most straightforward API. It usess auth source A and retrieves a value
from a single http call.

.. code-block::python
    :caption: api_1
    from requests import get
    from oauth2 import get_token_service_A
