Contributing
============

Since this project is a pytest plug-in, it really does require test-driven development.
If you want to contribute a bug fix or new feature, please first create a test case that
demonstrates what your new code is supposed to do. Note that you need to set up tests
using the pytester_ fixture, rather than testing directly.

This project uses hatch_ for its environments and build system, as well as pre-commit_,
ruff_, mdformat_, and docstrfmt_ for formatting and linting. Before you send in a pull
request, please:

- Set up ``pre-commit`` and use it to run ``ruff`` and ``mdformat`` with
  the settings included in the ``pyproject.toml`` and ``.pre-commit-config.yaml`` files
- Run tests using the command ``hatch run test:test``, which will run all of the tests
  against CPython 3.9-3.12 and Pytest 7.4.x, 8.2.x, and 8.3.x.
- Check test coverage with ``hatch run cov``
- Generate and proofread docs by running ``hatch run docs:generate``

Within the Github repo, actions are set up so that:

- Creating a tag that starts with "release-..." will trigger a release action.
- Creating a tag that starts with "docs-..." will trigger a documentation update.

.. _docstrfmt: https://github.com/LilSpazJoekp/docstrfmt

.. _hatch: https://github.com/pypa/hatch

.. _mdformat: https://github.com/executablebooks/mdformat

.. _pre-commit: https://pre-commit.com/

.. _ruff: https://github.com/astral-sh/ruff

.. _pytester: https://docs.pytest.org/en/stable/how-to/writing_plugins.html#testing-plugins
