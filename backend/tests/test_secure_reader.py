"""Regression tests for descriptor-relative read-only project access."""

import os
from pathlib import Path

import pytest

from app.projects.secure_reader import ProjectReadDenied, read_project_file


pytestmark = pytest.mark.skipif(
    os.name != "posix" or not hasattr(os, "O_NOFOLLOW"),
    reason="Secure reader is available only on POSIX systems with O_NOFOLLOW.",
)


def test_reads_regular_file_inside_project(tmp_path: Path) -> None:
    """Authorized in-root content must be readable."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    (project_root / "hello.txt").write_bytes(b"hello")
    assert read_project_file(project_root, "hello.txt") == b"hello"


@pytest.mark.parametrize(
    "unsafe_path",
    ["../secret.txt", "/etc/passwd", "folder/../secret.txt", "./hello.txt", "folder//x", ""],
)
def test_rejects_unsafe_paths(tmp_path: Path, unsafe_path: str) -> None:
    """Traversal, absolute paths and malformed components must fail closed."""
    with pytest.raises(ProjectReadDenied):
        read_project_file(tmp_path, unsafe_path)


def test_rejects_symlink_file(tmp_path: Path) -> None:
    """Symlinks must not redirect reads outside the project."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    outside_file = tmp_path / "private.txt"
    outside_file.write_bytes(b"private")
    (project_root / "link.txt").symlink_to(outside_file)
    with pytest.raises(ProjectReadDenied):
        read_project_file(project_root, "link.txt")


def test_rejects_symlink_directory(tmp_path: Path) -> None:
    """Intermediate directory symlinks must be rejected."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    outside_directory = tmp_path / "outside"
    outside_directory.mkdir()
    (outside_directory / "private.txt").write_bytes(b"private")
    (project_root / "linked").symlink_to(outside_directory, target_is_directory=True)
    with pytest.raises(ProjectReadDenied):
        read_project_file(project_root, "linked/private.txt")


def test_rejects_oversized_file(tmp_path: Path) -> None:
    """A file larger than the configured budget must not be returned."""
    (tmp_path / "large.txt").write_bytes(b"12345")
    with pytest.raises(ProjectReadDenied):
        read_project_file(tmp_path, "large.txt", max_bytes=4)


def test_rejects_directory_as_file(tmp_path: Path) -> None:
    """Directory handles must not be treated as regular files."""
    (tmp_path / "folder").mkdir()
    with pytest.raises(ProjectReadDenied):
        read_project_file(tmp_path, "folder")


def test_rejects_negative_budget(tmp_path: Path) -> None:
    """Invalid resource limits must be rejected before accessing the filesystem."""
    with pytest.raises(ProjectReadDenied):
        read_project_file(tmp_path, "anything", max_bytes=-1)
