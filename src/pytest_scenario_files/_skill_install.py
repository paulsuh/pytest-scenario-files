"""Console-script entry point that installs the bundled Claude Code skill.

This module has no dependency on anything else in this package at import
time other than the standard library, so it stays cheap to import even for
users who never run the command.
"""

from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

_SKILL_NAME = "pytest-scenario-files"


def _bundled_skill_dir() -> Path:
    """Return the path to the skill data shipped inside this installed package."""
    return Path(__file__).parent / "_skill_data"


def _default_install_dir() -> Path:
    return Path.home() / ".claude" / "skills" / _SKILL_NAME


def _dirs_are_identical(a: Path, b: Path) -> bool:
    """Recursively compare two directory trees for identical content."""
    comparison = filecmp.dircmp(a, b)
    if comparison.left_only or comparison.right_only or comparison.diff_files or comparison.funny_files:
        return False
    return all(_dirs_are_identical(a / sub, b / sub) for sub in comparison.common_dirs)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    force = "--force" in argv or "-f" in argv

    source = _bundled_skill_dir()
    if not source.is_dir():
        print(
            f"error: no bundled skill data found at {source}. "
            "This install may be missing package data (e.g. an editable/sdist install "
            "that predates the skill being added).",
            file=sys.stderr,
        )
        return 1

    destination = _default_install_dir()

    if destination.exists():
        if _dirs_are_identical(source, destination):
            print(f"'{_SKILL_NAME}' skill is already up to date at {destination}.")
            return 0
        if not force:
            print(
                f"A different version of the '{_SKILL_NAME}' skill already exists at "
                f"{destination}.\nRe-run with --force to overwrite it, or remove it "
                f"yourself first if you have local changes you want to keep.",
                file=sys.stderr,
            )
            return 1
        shutil.rmtree(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    print(f"Installed the '{_SKILL_NAME}' skill to {destination}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
