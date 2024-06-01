Contributing
============

Since this project is a pytest plug-in, it really does require test-driven development.
If you want to contribute a bug fix or new feature, please first create a test case that
demonstrates what your new code is supposed to do. Note that you need to set things up
using the ``pytester`` fixture, rather than testing directly.

This project uses hatch_ for its environments and build system, as well as pre-commit_,
ruff_, mdformat_, and docstrfmt_ for formatting and linting. Before you send in a pull
request, please:

- Set up ``pre-commit`` and use it to run ``ruff``, ``mdformat``, and ``docstrfmt`` with
  the settings included in the ``pyproject.toml`` and ``.pre-commit-config.yaml`` files
- Run tests using the command ``hatch run test:test``, which will run all of the tests
  against CPython 3.9-3.12 and PyPy 3.9-3.10
- Check test coverage with ``hatch run cov``

.. _docstrfmt: https://github.com/LilSpazJoekp/docstrfmt

.. _hatch: https://github.com/pypa/hatch

.. _mdformat: https://github.com/executablebooks/mdformat

.. _pre-commit: https://pre-commit.com/

.. _ruff: https://github.com/astral-sh/ruff
