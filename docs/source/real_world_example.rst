A Real World Example
====================

This is a slightly simplified and anonymized real world example of how you
might use this plug-in. This shows how you can use pytest-scenario-files to:

- Feed URLs to the Responses package
- Chain URL sections together for deeper unit tests

Our application calls multiple APIs, each of which uses OAuth2 for authentication
and authorization. However, while some of them share one authentication URL and
service account credentials, others use a different URL and credentials. To
get the service account credentials, we need to make a call into a lambda layer
that communicates on 127.0.0.1:8200 using http (not https!).

We want to test successful and unsuccessful cases of each API call, and for a
variety of reasons. There are many URLs to keep track of and parameterize
into a prethora of scenarios. Trying to do this using standard pytest
parameterization would be a lot of work.

The Example Code
----------------

All of these files are available in the repository in the XXXXXX folder.

.. toctree::
    :titlesonly:

    real_world_example/oauth
    real_world_example/api
