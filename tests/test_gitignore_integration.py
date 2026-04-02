# File: tests/test_gitignore_integration.py

"""Tests for optional pathspec-backed gitignore support."""

from __future__ import annotations

import builtins
import importlib.util
from pathlib import Path

import pytest

from annot8.git_integration import get_gitignore_patterns, is_gitignored


def test_get_gitignore_patterns_matches_repository_rules(tmp_path: Path) -> None:
    """Load .gitignore rules and match relative paths against them."""
    (tmp_path / ".git").mkdir()
    (tmp_path / ".gitignore").write_text(
        "node_modules/\n*.log\n!important.log\n",
        encoding="utf-8",
    )

    spec = get_gitignore_patterns(tmp_path)

    assert spec is not None
    assert is_gitignored(tmp_path / "node_modules" / "left-pad.js", tmp_path, spec)
    assert is_gitignored(tmp_path / "debug.log", tmp_path, spec)
    assert not is_gitignored(tmp_path / "important.log", tmp_path, spec)


def test_git_integration_imports_without_pathspec(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The module should still import when the optional dependency is absent."""
    source_path = Path(__file__).resolve().parents[1] / "src" / "annot8" / "git_integration.py"
    module_name = "annot8_git_integration_without_pathspec"
    original_import = builtins.__import__

    def guarded_import(name, module_globals=None, module_locals=None, fromlist=(), level=0):
        if name == "pathspec" or name.startswith("pathspec."):
            raise ImportError("pathspec is not installed")
        return original_import(name, module_globals, module_locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    spec = importlib.util.spec_from_file_location(module_name, source_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.PATHSPEC_AVAILABLE is False
    assert module.get_gitignore_patterns(tmp_path) is None
