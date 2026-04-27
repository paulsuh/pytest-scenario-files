# AI Skill Generation Prompt

This prompt is designed to guide an AI agent through the process of
transforming a standard documentation directory (e.g., Sphinx/RST) into
a high-performance, context-optimized AI Skill folder.

______________________________________________________________________

## The Prompt

**Goal**: Transform the source documentation in `docs/source/` into a
structured, optimized AI Skill directory adhering to the `SKILL.md`
standard.

**Process**:

### 1. Source Analysis & Assembly

- **Ordering**: Parse `index.rst` to determine the correct logical flow
  of the documentation.
- **Dynamic Content**: If the documentation uses dynamic directives like
  `automodule` or `autodoc`, execute the build process (e.g.,
  `hatch run docs:generate` or `make html`) to resolve them.
- **Conversion**: Convert all RST or generated HTML files into clean
  Markdown. Strip Sphinx-specific noise (breadcrumbs, "Next/Previous"
  links, "Contents" directives).
- **Consolidation**: Combine the files into a single temporary "source
  of truth" document for easier analysis.

### 2. Context Window Optimization (Trimming & Cleaning)

- **Remove Fluff**: Strip conversational filler, repetitive introductory
  text, and historical "About" sections that don't assist in code
  generation.
- **Filter Content**: Remove developer-focused docs (e.g.,
  `contributing.rst`) and purely technical API references generated from
  source (e.g., `api.rst`) that are redundant or too noisy for a
  usage-focused skill.
- **Merge Small Files**: Sections like 'Installation' and 'Basic Usage'
  should be merged directly into the main `SKILL.md` to reduce
  file-loading overhead.
- **Simplify Examples**: Optimize code blocks to be concise but
  technically complete.
- **Technical Verification**: Cross-reference the documentation with the
  actual source code (e.g., `plugin.py`) to ensure parameter names,
  signatures, and flags are accurate.

### 3. Structural Transformation

Create a directory named `[project-name]-skill/` with a `references/`
subdirectory.

#### SKILL.md (The Entry Point)

- **YAML Frontmatter**: Include `name` and a high-signal `description`
  (what it does + when to use it).
- **Core Sections**:
  - `## Core Features`
  - `## Installation`
  - `## Basic Usage` (High-level quickstart)
  - `## When to use this skill` (Actionable triggers for the AI)
  - `## Reference Documentation` (Markdown links to files in
    `references/`)

#### References (Deep Dives)

- Split advanced topics and specialized integrations into separate files
  in `references/`.
- Ensure each reference file is focused and trimmed of any non-essential
  context.

### 4. Final Validation

- Ensure no broken internal links.
- Check that the main `SKILL.md` is under ~150 lines for fast initial
  context loading.
- Verify that the combined skill accurately represents the project's
  current state.

______________________________________________________________________

## Example Workflow (Meta-Instructions)

When executing this prompt:

1. **Explore**: List `docs/source/` and read `index.rst`.
2. **Resolve**: Build the docs if needed to resolve dynamic content, but
   skip processing `api.rst`.
3. **Draft**: Create the modular structure incrementally.
4. **Refine**: Apply trimming passes to each file to minimize token
   usage without losing technical accuracy.
