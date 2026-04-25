---
name: pytest-scenario-files

description: A pytest plugin that automates loading test scenarios from JSON/YAML files into parameterized fixtures. Use it when test data is too large for source code, to separate data from logic, or to reuse data across tests via file-based references.
---

# pytest-scenario-files

`pytest-scenario-files` is a `pytest` plugin that runs unit test scenarios using data loaded from files. It makes managing large amounts of test data easier by separating it from the test code.

## Core Features

- Loads data for scenarios from files into fixtures.
- Data files are matched with tests by a naming convention.
- Multiple scenario data sets may be in one file.
- Fixtures may refer to fixtures in other files.
- Supports indirect parameterization.
- Integration with Responses and Respx mocking packages.

## Installation

This plug-in can be installed from PyPI using `pip`:

```bash
pip install pytest-scenario-files
```

If you want to utilize the Responses or Respx integration, specify the corresponding extra:

```bash
pip install pytest-scenario-files[responses]
pip install pytest-scenario-files[respx]
```

## When to use this skill

Use this skill when you need to:
- Understand how `pytest-scenario-files` works.
- Set up or configure the plugin.
- Create or debug data files for test scenarios.
- Use advanced features like loading by reference or indirect parameterization.
- Integrate with Responses or Respx for HTTP mocking in scenarios.

## Reporting Issues

If you encounter any problems, please [file an issue](https://github.com/paulsuh/pytest-scenario-files/issues) including a detailed description and an example of the problem.

## Reference Documentation

Detailed documentation is available in the `references/` directory:

- [Basic Usage](references/basic_usage.md): How to set up fixtures and create data files.
- [Advanced Usage](references/advanced_usage.md): Merging test cases, loading by reference, and the `psf_expected_result` fixture.
- [Responses Integration](references/responses_integration.md): Detailed guide on using Responses with scenario files.
- [Respx Integration](references/respx_integration.md): Detailed guide on using Respx with scenario files.
- [API Reference](references/api.md): Detailed documentation of fixtures and hooks.
