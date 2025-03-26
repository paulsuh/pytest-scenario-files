Installation
============

This plug-in can be installed from PyPI using ``pip``, with the command:

.. code-block::

    pip install pytest-scenario-files

That's all! No additional settings or flags, no need to add import statements or
decorators to your tests.

If you want to utilize the Responses integration you can either install
the Responses package separately or specify the Responses extra:

.. code-block::

    pip install pytest-scenario-files[responses]

Similarly, if you want to utilize the Respx integration you can either
install the Respx package directly or you can specify the Respx extra:

.. code-block::

    pip install pytest-scenario-files[respx]
