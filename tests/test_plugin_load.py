"""The most basic test.

See if the plug-in has loaded via the entrypoint by looking in the output
of pytest's help.
"""


def test_plugin_load(pytestconfig):
    # not so important in and of itself, but this test serves as a check that the
    # plugin loaded correctly
    plugin_manager = pytestconfig.pluginmanager
    assert plugin_manager.has_plugin("pytest_scenario_files")
