"""Tests for the pytest-scenario-files-install-skill console script."""

from __future__ import annotations

import pytest

from pytest_scenario_files import _skill_install


@pytest.fixture
def bundled_skill_dir(tmp_path, monkeypatch):
    """Point the installer at a throwaway bundled-skill source directory."""
    source = tmp_path / "bundled"
    (source / "references").mkdir(parents=True)
    (source / "SKILL.md").write_text("# skill\n")
    (source / "references" / "notes.md").write_text("notes\n")
    monkeypatch.setattr(_skill_install, "_bundled_skill_dir", lambda: source)
    return source


@pytest.fixture
def install_dir(tmp_path, monkeypatch):
    """Point the installer's default destination at a throwaway directory."""
    destination = tmp_path / "home" / ".claude" / "skills" / "pytest-scenario-files"
    monkeypatch.setattr(_skill_install, "_default_install_dir", lambda: destination)
    return destination


def test_main_installs_into_fresh_destination(bundled_skill_dir, install_dir, capsys):
    result = _skill_install.main([])

    assert result == 0
    assert (install_dir / "SKILL.md").read_text() == "# skill\n"
    assert (install_dir / "references" / "notes.md").read_text() == "notes\n"
    assert "Installed" in capsys.readouterr().out


def test_main_is_a_noop_when_already_up_to_date(bundled_skill_dir, install_dir, capsys):
    _skill_install.main([])
    capsys.readouterr()

    result = _skill_install.main([])

    assert result == 0
    assert "already up to date" in capsys.readouterr().out


def test_main_refuses_to_overwrite_conflicting_install_without_force(bundled_skill_dir, install_dir, capsys):
    install_dir.mkdir(parents=True)
    (install_dir / "SKILL.md").write_text("# a different, locally-modified skill\n")

    result = _skill_install.main([])

    assert result == 1
    assert (install_dir / "SKILL.md").read_text() == "# a different, locally-modified skill\n"
    assert "Re-run with --force" in capsys.readouterr().err


@pytest.mark.parametrize("flag", ["--force", "-f"])
def test_main_overwrites_conflicting_install_with_force(bundled_skill_dir, install_dir, capsys, flag):
    install_dir.mkdir(parents=True)
    (install_dir / "SKILL.md").write_text("# a different, locally-modified skill\n")

    result = _skill_install.main([flag])

    assert result == 0
    assert (install_dir / "SKILL.md").read_text() == "# skill\n"
    assert "Installed" in capsys.readouterr().out


def test_main_errors_when_bundled_skill_data_is_missing(tmp_path, monkeypatch, install_dir, capsys):
    missing_source = tmp_path / "does-not-exist"
    monkeypatch.setattr(_skill_install, "_bundled_skill_dir", lambda: missing_source)

    result = _skill_install.main([])

    assert result == 1
    assert not install_dir.exists()
    assert "no bundled skill data found" in capsys.readouterr().err
