::: {#module-pytest_scenario_files .section} []{#api}

# API

Package that will generate Pytest unit test scenarios based on data
files.

pytest_scenario_files.**psf_expected_result**``` (]{.sig-paren}*request``: ```\]{.p}` ]{.w}`FixtureRequest`*`)
\[ -> \[\[AbstractContextManager\`\`

: Convenience fixture for possible expected exceptions

```
Pytest has a pattern called Parameterized Conditional Raising (See:
[https://docs.pytest.org/en/8.3.x/example/parametrize.html#parametrizing-conditional-raising](https://docs.pytest.org/en/8.3.x/example/parametrize.html#parametrizing-conditional-raising){.reference
.external}). This fixture allows the user to specify either an
expected exception (including a match string or regexp) in the
scenario file, or any other expected result value. An exception gets
wrapped in a pytest.raises() context manager, while any other value
gets wrapped in a nullcontext() context manager. The test function
can then use a call like:

:::: {.highlight-default .notranslate}
::: highlight
    with psf_expected_result as expected_result:
        assert expected_result == function_being_tested()
:::
::::

Parameters:

:   **request** (*pytest.FixtureRequest*) -- The fixture request
    object containing the test parameters.

Returns:

:   A context manager that either catches the expected exception or
    a nullcontext() context manager.

Return type:

:   AbstractContextManager:
```

<!-- -->

pytest_scenario_files.**psf_responses**``` (]{.sig-paren}*request``: ```\]{.p}\`
\]{.w} None````  None```\] ````\]{.sig-return}

: Returns a responses.RequestsMock with scenario data loaded.

```
Used for integration with the Responses package. Each test scenario
will get its own active RequestsMock object. This object can then be
updated at runtime to override the responses loaded from files.
```

<!-- -->

pytest_scenario_files.**psf_respx_mock**``` (]{.sig-paren}*request``: ```\]{.p}\`
\]{.w} None````  None```\] ````\]{.sig-return}

: Returns a respx.MockRouter with scenario data loaded.

```
Used for integration with the Respx package. Each test scenario will
get its own active MockRouter object. This object can then be
updated at runtime to override the responses loaded from files.
```

<!-- -->

pytest_scenario_files.**pytest_addoption**``` (]{.sig-paren}*parser``: ```\]{.p}` ]{.w}[[Parser`\*,
*`pluginmanager`*\[)

: Pytest hook function that adds the command line options.

```
Adds the command line options to automatically load http responses
for the Responses package or the Respx package and additional
options whether to require all responses to be fired and all calls
to be mocked.
```

<!-- -->

pytest_scenario_files.**pytest_configure**``` (]{.sig-paren}*config``: ```\]{.p}` ]{.w}[[Config`\*\[)

: Get config data from command line flags

```
Raises an exception if both --psf-load-responses and
--psf-load-respx are both enabled since these are mutually exclusive
options. Also stores values for psf-fire-all-responses,
psf-assert-all-fired, and psf-assert-all-mocked.

Parameters:

:   **config** (*pytest.Config*) -- The pytest configuration object
    containing all command-line options and plugin configuration.

Raises:

:   **pytest.UsageError** -- If both --psf-load-responses and
    --psf-load-respx options are specified simultaneously.
```

<!-- -->

pytest_scenario_files.**pytest_generate_tests**``` (]{.sig-paren}*metafunc``: ```\]{.p}` ]{.w}`Metafunc`*`)
\[ -> \[\[None\`\`

: Pytest hook function that does the parameterization.

```
This is where the heavy lifting is done. The process is:

1.  Walk the directory tree looking for files that match the name of
    the test.

2.  Load test data from the files.

3.  Extract fixture names and check for consistency.

4.  (Optional) Gather data from all fixtures with the suffixes
    ``_response`{.docutils .literal .notranslate}` or
    ``_responses`{.docutils .literal .notranslate}` into a
    single fixture for use with the Responses or Respx integrations.

5.  Get list of indirect fixtures and remove the suffix
    ``_indirect`{.docutils .literal .notranslate}` from
    indirect fixture names.

6.  Reformat the data into lists for the parameterization call.

7.  Make the function call.

Parameters:

:   **metafunc** -- Pytest fixture used to create the
    parameterization
```

::: :::::::

::::::::: related-pages [](contributing.html){.next-page}

::::: page-info ::: context Next :::

::: title Contributing ::: :::::

!\[\](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZnVyby1yZWxhdGVkLWljb24iPjx1c2UgaHJlZj0iI3N2Zy1hcnJvdy1yaWdodCIgLz48L3N2Zz4=){.furo-related-icon}
[!\[\](data:image/svg+xml;base64,PHN2ZyBjbGFzcz0iZnVyby1yZWxhdGVkLWljb24iPjx1c2UgaHJlZj0iI3N2Zy1hcnJvdy1yaWdodCIgLz48L3N2Zz4=){.furo-related-icon}](respx_integration.html){.prev-page}

::::: page-info ::: context Previous :::

::: title Respx Integration ::: ::::: :::::::::

:::::: bottom-of-page :::: left-details ::: copyright Copyright © 2024,
2025 Paul Suh :::

Made with [Sphinx](https://www.sphinx-doc.org/) and
[@pradyunsg](https://pradyunsg.me){.muted-link}'s
[Furo](https://github.com/pradyunsg/furo) ::::

::: right-details ::: :::::: :::::::::::::::::::

:::::: {.toc-sticky .toc-scroll} ::: toc-title-container \[ On this page
\]{.toc-title} :::

:::: toc-tree-container ::: toc-tree

- [API](#){.reference .internal}
  - [\[`psf_expected_result()`{.docutils .literal .notranslate}\]{.pre}](#pytest_scenario_files.psf_expected_result){.reference
    .internal}
  - [\[`psf_responses()`{.docutils .literal .notranslate}\]{.pre}](#pytest_scenario_files.psf_responses){.reference
    .internal}
  - [\[`psf_respx_mock()`{.docutils .literal .notranslate}\]{.pre}](#pytest_scenario_files.psf_respx_mock){.reference
    .internal}
  - [\[`pytest_addoption()`{.docutils .literal .notranslate}\]{.pre}](#pytest_scenario_files.pytest_addoption){.reference
    .internal}
  - [\[`pytest_configure()`{.docutils .literal .notranslate}\]{.pre}](#pytest_scenario_files.pytest_configure){.reference
    .internal}
  - [\[`pytest_generate_tests()`{.docutils .literal .notranslate}\]{.pre}](#pytest_scenario_files.pytest_generate_tests){.reference
    .internal} ::: :::: :::::: ::::::::::::::::::::::::
    :::::::::::::::::::::::::::::::::::::
