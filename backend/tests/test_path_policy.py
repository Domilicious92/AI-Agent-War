"""Tests for the initial fail-closed project path policy."""

from pathlib import Path

import pytest

from app.projects.path_policy import ProjectPathDenied, resolve_project_path


def test_accepts_file_within_authorized_project(tmp_path: Path) -> None:
    """An existing in-project file should resolve to its canonical path."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    allowed_file = project_root / "README.md"
    allowed_file.write_text("allowed", encoding="utf-8")

    assert resolve_project_path(project_root, Path("README.md")) == allowed_file


def test_rejects_parent_directory_traversal(tmp_path: Path) -> None:
    """Relative traversal must not escape the project root."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    outside_file = tmp_path / "private.txt"
    outside_file.write_text("private", encoding="utf-8")

    with pytest.raises(ProjectPathDenied):
        resolve_project_path(project_root, Path("../private.txt"))


def test_rejects_absolute_outside_path(tmp_path: Path) -> None:
    """Absolute paths outside the authorized root must be denied."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    outside_file = tmp_path / "private.txt"
    outside_file.write_text("private", encoding="utf-8")

    with pytest.raises(ProjectPathDenied):
        resolve_project_path(project_root, outside_file)


def test_rejects_symlink_escape(tmp_path: Path) -> None:
    """A symlink pointing outside the root must not bypass validation."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    outside_file = tmp_path / "private.txt"
    outside_file.write_text("private", encoding="utf-8")
    link_path = project_root / "link.txt"
    try:
        link_path.symlink_to(outside_file)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks are unavailable on this filesystem.")

    with pytest.raises(ProjectPathDenied):
        resolve_project_path(project_root, Path("link.txt"))


def test_rejects_nonexistent_file(tmp_path: Path) -> None:
    """A missing path must fail closed rather than silently being created."""
    project_root = tmp_path / "project"
    project_root.mkdir()

    with pytest.raises(ProjectPathDenied):
        resolve_project_path(project_root, Path("missing.txt"))
