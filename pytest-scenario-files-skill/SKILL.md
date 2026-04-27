---
name: pytest-scenario-files
description: A pytest plugin for running unit test scenarios using data loaded from YAML or JSON files, with built-in support for Responses and Respx mocking.
---

## Core Features
- **Auto-Loading**: Automatically loads scenario data from YAML/JSON files into pytest fixtures.
- **Convention-Based**: Matches files to tests using `data_<test_name_without_test_prefix>.yaml`.
- **Scalable**: Supports multiple scenarios per file, multiple files per test, and directory-based discovery.
- **Data Referencing**: Share data across files using the `__Filename:test_id:fixture` syntax.
- **Indirect Parameterization**: Mark fixtures for indirect parameterization with the `_indirect` suffix.
- **Mocking Integration**: Native support for loading `Responses` and `Respx` mocks directly from scenario files.

## Installation
```bash
pip install pytest-scenario-files

# To include mocking support:
pip install pytest-scenario-files[responses]
pip install pytest-scenario-files[respx]
```

## Basic Usage
1. **Test Function**: Accept fixtures that correspond to keys in your data file.
   ```python
   def test_calculate(input_val, expected):
       assert my_func(input_val) == expected
   ```
2. **Data File**: Create a file named `data_calculate.yaml` in the test's directory (or a subdirectory).
   ```yaml
   scenario_one:
     input_val: 10
     expected: 20
   scenario_two:
     input_val: 5
     expected: 10
   ```
3. **Execution**: Run `pytest` normally. The plugin discovers the file and parameterizes `test_calculate` into two cases: `test_calculate[scenario_one]` and `test_calculate[scenario_two]`.

## Tips & Cautions
- **Regular Fixtures**: If a fixture is defined in both a data file and your test code (or `conftest.py`), the data file value takes precedence. To use a standard fixture alongside scenarios, simply omit it from the data file.
- **Naming Conflicts**: Beware of test names that are extensions of each other (e.g., `test_foo` and `test_foo_bar`). A file named `data_foo_bar.yaml` will be loaded for *both* tests. To avoid this, use unique names or separate directories.

## When to use this skill
- Use when test data is large, complex, or numerous, making in-code parameterization messy.
- Use to decouple test logic from test data.
- Use when you need to manage complex HTTP mock responses (JSON/YAML) externally.
- Use to avoid repetitive test code by leveraging data merging and referencing.

## Reference Documentation
- [Advanced Usage](references/advanced_usage.md): Data merging, cross-references, indirect parameterization, and the `psf_expected_result` fixture.
- [Responses Integration](references/responses_integration.md): Mocking `requests` with external data.
- [Respx Integration](references/respx_integration.md): Mocking `httpx` with external data.
