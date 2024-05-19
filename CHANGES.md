# Change Log

#### 1.0 - 2024-05-19

Bump version to 1.0 and set Development Status to `5 - 
Production/Stable`

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
