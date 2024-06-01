..
    Pytest Scenario Files documentation master file, created by
    sphinx-quickstart on Tue May 21 23:42:46 2024.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

pytest-scenario-files
=====================

*Making Pytest Scenarios Easy and Scalable*

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

Compatibility
-------------

This package is a plug-in for ``pytest`` and works with Python 3.9 and up.

- Tested with ``pytest`` version 7.4.x, should work with any version 6.2.5 or higher
- Tested with CPython 3.9-3.12 and PyPy 3.9-3.10

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    installation
    basic_usage
    advanced_usage
    contributing
    About <about>