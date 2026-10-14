import warnings
from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import nullcontext
from json import load
from os.path import join
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, NamedTuple, Union, cast

import pytest
from yaml import safe_load

if TYPE_CHECKING:
    from responses import RequestsMock
    from respx import MockResponse, MockRouter


# configuration flag holding space
class _PsfConfigTuple(NamedTuple):
    psf_load_responses: bool
    psf_fire_all_responses: bool
    psf_load_respx: bool
    psf_assert_all_called: bool
    psf_assert_all_mocked: bool


_config_keys = (
    ("psf-load-responses", "Automatically load data for Responses from scenario files"),
    ("psf-fire-all-responses", "Are all responses required to be fired (for Responses)?"),
    ("psf-load-respx", "Automatically load data for Respx from scenario files"),
    ("psf-assert-all-called", "Are all responses required to be fired (for Respx)?"),
    ("psf-assert-all-mocked", "Are all Httpx calls required to be mocked (for Respx)?"),
)


_psf_configs: _PsfConfigTuple


# Need to use a NamedTuple as the key for the routing dict
# Can't use a dict as a dict can't be a dict key (unless you
# do funky stuff to make it immutable).
class _RespxRouteKey(NamedTuple):
    method: str
    url: str


class BadTestCaseDataException(Exception):
    """An exception class used to mark bad test case data."""

    pass


def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
    """Pytest hook function that adds the command line options.

    Adds the command line options to automatically load http responses for the Responses
    package or the Respx package and additional options whether to require all responses
    to be fired and all calls to be mocked.

    """
    option_group = parser.getgroup("Pytest Scenario Files", "Options for the pytest-scenario-files plug-in")
    for opt, help_text in _config_keys:
        option_group.addoption(
            f"--{opt}",
            action="store_true",
            default=False,
            dest=opt,
            help=help_text,
        )


def pytest_configure(config: pytest.Config) -> None:
    """Get config data from command line flags

    Raises an exception if both `--psf-load-responses` and `--psf-load-respx` are both
    enabled since these are mutually exclusive options. Also stores values for
    `psf-fire-all-responses`, `psf-assert-all-fired`, and `psf-assert-all-mocked`.

    :param pytest.Config config: The pytest configuration object containing all
        command-line options and plugin configuration.

    :raises pytest.UsageError: If both `--psf-load-responses` and `--psf-load-respx`
        options are specified simultaneously.

    """
    global _psf_configs
    _psf_configs = _PsfConfigTuple(*(config.getoption(opt) for opt, _ in _config_keys))
    if _psf_configs.psf_load_responses and _psf_configs.psf_load_respx:
        raise pytest.UsageError("The --psf-load-resposes and --psf-load-respx options are mutually exclusive.")


def _load_test_data_from_file(filepath: str) -> dict[str, Any]:
    """Load test data from a file and return it as a dictionary.

    :param str filepath: The path of the file to load.

    :returns: The loaded test data as a dictionary.
    :rtype: dict[str, Any]

    :raises BadTestCaseDataException: If the loaded test case data are of the incorrect
        format.

    """
    with open(filepath) as fp:
        if filepath.endswith(".json"):
            test_data = load(fp)
        elif filepath.endswith((".yaml", ".yml")):
            test_data = safe_load(fp)
        else:
            raise BadTestCaseDataException(f"{filepath} does not have an extension of .json, .yaml, or .yml.")

        if not isinstance(test_data, dict):
            raise BadTestCaseDataException(f"{filepath} did not produce a dictionary when loaded.")

        for case_name, case_data in test_data.items():
            if not isinstance(case_data, dict):
                raise BadTestCaseDataException(f"From {filepath}: data for test case {case_name} is not a dict. ")

        _load_referenced_data(test_data)

        return test_data
