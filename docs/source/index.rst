..
    Pytest Scenario Files documentation master file, created by
    sphinx-quickstart on Tue May 21 23:42:46 2024.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

pytest-scenario-files
=====================

*Making Pytest Scenarios Easy and Scalable*

|Python versions badge| |Pytest Plug-in badge|

|Hatch badge| |Ruff badge| |Pre-commit badge|

``pytest-scenario-files`` is a ``pytest`` plugin that runs unit test scenarios using
data loaded from files.

Features
--------

- Loads data for scenarios from files into fixtures
- Data files are matched with tests by a naming convention
- Multiple scenario data sets may be in one file
- There may be multiple data files for each test
- Fixtures may refer to fixtures in other files
- Can specify indirect parameterization
- Intuitive and sane data file structure
- Integration with Responses mocking package for Requests
- NEW - Integration with the Respx mocking package for Httpx

Compatibility
-------------

This package is a plug-in for Pytest and works with Python 3.9 and up.

- Tested with Pytest versions 7.4, 8.2 and 8.3
- Tested with CPython 3.9–3.13
- Tested with Responses 0.25.7
- Tested with Respx 0.22.0

.. toctree::
    :maxdepth: 2
    :caption: Contents:
    :hidden:

    installation
    basic_usage
    advanced_usage
    responses_integration
    respx_integration
    api
    contributing
    About <about>

.. |Python versions badge|  image:: https://img.shields.io/pypi/pyversions/pytest-scenario-files.svg
                            :alt: Compatible Python versions badge

.. |Pytest Plug-in badge|   image:: https://img.shields.io/badge/Pytest-Plug--in-orange?logo=Pytest
                            :alt: Pytest Plug-in badge

.. |Hatch badge|            image:: https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg
                            :alt: Hatch badge

.. |Ruff badge|             image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
                            :alt: Ruff badge

.. |Pre-commit badge|       image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
                            :alt: Pre-commit badge
