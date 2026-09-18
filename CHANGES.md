# Change Log

#### 1.3.3 - 2026-09-XX (unreleased)

- Remove support for Python 3.10, add support for Python 3.15.
- Update tests to ensure compatibility with pytest 9.1.
- Miscellaneous documentation updates.
- Add `--psf-reference-root` command line/ini option and a
  `psf_reference_root` module-level variable in the test file to pin the
  search root used to resolve `__file:scenario:fixture` data references.
  The CLI option takes priority over the test-file variable. A
  configured root is exclusive: if the reference isn't found there,
  resolution fails with a clear error rather than silently falling back
  elsewhere.
- Fix `_load_referenced_data()` to search the referencing file's own
  directory before falling back to the current working directory, so a
  stray duplicate of a referenced data file elsewhere under cwd no
  longer causes a spurious merge conflict.
- Raise `BadTestCaseDataException` (naming the referencing file, the
  reference, and every root searched) instead of a bare `KeyError` when
  a `__file:scenario:fixture` reference cannot be resolved.

#### 1.3.2 - 2026-05-17

- Add support for generating an SBOM file and add an SBOM file to the
  package.
- Remove testing and metadata for Python 3.9.

#### 1.3.1 - 2026-02-16

- Update tests to ensure compatibility with pytest 9.0 and CPython 3.14.
- Skip pytest 8.2 and 8.3 checks.
- Use built-in Hatch test environment since matrix now works properly.
- Edit documentation to reflect the updated tests.

#### 1.3.0 - 2025-09-02

- Add loading of native Responses files.

#### 1.2.1 - 2025-08-11

- Update tests to ensure compatibility with pytest 8.4.
- No change to the code, and thus no change to the version number.
- Edit documentation to reflect the updated tests.
- Fix the CI/CD GitHub Actions workflows for publishing.

#### 1.2.1 - 2025-05-20

- Fix a bug where if you have a test that doesn't use the psf_responses
  fixture and the --psf-load-responses flag is used, the test will fail
  with an error, `functions uses no fixture 'psf_responses'`.

#### 1.2 - 2025-05-12

- Add integration with Respx for testing httpx.

#### 1.1 - 2024-11-21

- Add integration with Responses.
- Add convenience fixture psf_expected_result for parameterized
  conditional raising.
- Add detailed realistic(-ish) usage example.
- Add conditional Hatch testing matrix dependencies.

#### 1.0 - 2024-05-19

Bump version to 1.0 and set Development Status to
`5 - Production/Stable`

#### 0.12 - 2024-05-12

Rename to pytest_scenario_files

#### 0.11 - 2024-02-14

Add ability to specify indirect parameterization

#### 0.10.2 - 2024-02-09

Add additional test case for finding files by reference

#### 0.10.1 - 2024-02-08

Search the entire space for files that load data by reference instead of
assuming that the file will be found in the same subdirectory

#### 0.10 - 2024-01-27

- Change to using internal merge for data files
- Remove undocumented feature that directories that start with "." would
  not be searched for test data files
- Add expected fail test cases to 100% test coverage
- Remove dependency on `deepmerge`

#### 0.9.5 - 2024-01-25

Updates to documentation and formatting

#### 0.9.3 - 2024-01-24

Update how merging works

- Change merge strategy so that a conflict will raise an exception
- Correct the start directory for data file search
- Update documentation

#### 0.9 - 2024-01-22

Additional tests, examples, and documentation

#### 0.3 - 2024-01-20

Allow merging data for a test case from multiple files

- Introduce dependency on `deepmerge`

#### 0.2 - 2024-01-20

Change to multiple fixtures

- Load data into multiple fixtures rather than a single fixture
- Update tests and example code to work with the new paradigm

#### 0.1 - 2024-01-17

Initial checkpoint

- Load multiple test cases from one file
- Load multiple test cases from multiple files
- Unit tests via `pytester`
- Clean up unused files
