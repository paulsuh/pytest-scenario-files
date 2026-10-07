# Cross-file sharing: anchors vs. `__file:case:fixture` references

Two independent mechanisms exist for avoiding duplicated data, and they solve
different scopes:

- **YAML anchors/aliases** (`&name` / `*name`) — plain YAML, dedupes *within one
  file*. Define the shared block once on the first scenario, reference it from
  later scenarios in the same file:

  ```yaml
  scenario_one:
    mock_env_vars: &shared_env
      API_KEY: test-key
    expected_result: "one"

  scenario_two:
    mock_env_vars: *shared_env
    expected_result: "two"
  ```

- **Cross-file references** — a string value prefixed with two underscores,
  `__filename.yaml:case_id:fixture_name`, resolved by the plugin at load time. Useful
  for sharing a block *across* multiple data files, commonly by pulling several
  files' worth of scenarios from one `data_<module>_common.yaml`:

  ```yaml
  # data_foo_common.yaml
  common:
    base_url: https://api.example.com

  # data_foo_client.yaml
  scenario_one:
    base_url: __data_foo_common.yaml:common:base_url
  ```

  Reference resolution searches **from the current working directory** (i.e.
  wherever `pytest` was invoked), not from the referencing file's own directory —
  so a reference can reach a file anywhere in the project, not just nearby. There is
  no way to configure or restrict this search root in the current version of the
  plugin. Nothing prevents an infinite self-referential loop, so avoid a reference
  chain that could cycle back on itself.

Don't reference every field individually if you're pulling several values from a
common file — that defeats the point. Reference the values that are actually shared,
and keep scenario-specific values (expected results, error messages) local to the
file that uses them.

This is a different feature from the automatic, unconditional merging of every file
matching a test's name described in `references/data-file-mechanics.md` — that
mechanism merges whole files by scenario id, while this one is an explicit pointer
to one value in another file.
