A Real World Example
====================

This is a slightly simplified and anonymized real world example of how you
might use this plug-in. The purpose is to show how the features of
pytest-scenario-files work together to enable you the developer to generate
and test many different scenarios, and interact with common testing tools
like the Responses library.

The example shows how you can use pytest-scenario-files to:

- Feed URLs to the Responses package
- Chain fixtures together to build a more complete test structure

The Example Application
-----------------------

Our application calls multiple APIs, each of which uses OAuth2 for authentication
and authorization. However, while some of them share one authentication URL and
service account credentials, others use a different URL and credentials. To
get the service account credentials, we need to make a call into a lambda layer
that communicates on 127.0.0.1:8200 using http (not https!).

We want to test successful and unsuccessful cases of each API call, and for a
variety of reasons. There are many URLs to keep track of and parameterize
into a prethora of scenarios. Trying to do this using standard pytest
parameterization would be a lot of work.

All of these files are available in the repository in the ``docs/source/example_files``
folder. You can run the example tests by ``cd``'ing into that folder and the
running the command

.. code-block:: sh

    $ PYTHONPATH=. pytest -vv -rA

.. toctree::
    :titlesonly:
    :caption: Example docs

    real_world_example/oauth
    real_world_example/api
    real_world_example/testing_oauth
    real_world_example/testing_api
