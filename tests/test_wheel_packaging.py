"""Verify the built wheel bundles the Claude Code skill data.

These tests build a real wheel using the project's hatchling backend and
inspect its contents, guarding the ``[tool.hatch.build.targets.wheel.force-include]``
mapping in pyproject.toml that copies ``skills/pytest-scenario-files`` into
``pytest_scenario_files/_skill_data`` for ``_skill_install.py`` to find at runtime.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from hatchling.builders.wheel import WheelBuilder

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="module")
def built_wheel_path(tmp_path_factory):
    out_dir = tmp_path_factory.mktemp("wheel_out")
    builder = WheelBuilder(str(PROJECT_ROOT))
    (wheel_path,) = builder.build(directory=str(out_dir))
    return Path(wheel_path)


def test_wheel_bundles_skill_data(built_wheel_path):
    source_skill_dir = PROJECT_ROOT / "skills" / "pytest-scenario-files"
    expected_files = {
        f"pytest_scenario_files/_skill_data/{path.relative_to(source_skill_dir)}"
        for path in source_skill_dir.rglob("*")
        if path.is_file()
    }

    with zipfile.ZipFile(built_wheel_path) as wheel:
        packaged_files = {name for name in wheel.namelist() if "_skill_data" in name}

    assert packaged_files == expected_files


def test_wheel_skill_data_content_matches_source(built_wheel_path):
    source_skill_md = (PROJECT_ROOT / "skills" / "pytest-scenario-files" / "SKILL.md").read_text()

    with zipfile.ZipFile(built_wheel_path) as wheel:
        packaged_skill_md = wheel.read("pytest_scenario_files/_skill_data/SKILL.md").decode()

    assert packaged_skill_md == source_skill_md
