"""Package that will generate Pytest unit test scenarios based on data files."""

from .plugin import pytest_addoption, pytest_configure, pytest_generate_tests
