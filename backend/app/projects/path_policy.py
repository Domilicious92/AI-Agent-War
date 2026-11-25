"""Fail-closed path policy for a single explicitly authorized project root.

This module only validates paths; it does not grant filesystem permissions or
replace operating-system sandboxing. Callers must avoid time-of-check/time-of-use
races by using descriptor-relative operations in the eventual file worker.
"""

from pathlib import Path


class ProjectPathDenied(ValueError):
    """A requested path is not inside the authorized project root."""


def resolve_project_path(project_root: Path, requested_path: Path) -> Path:
    """Resolve a candidate and reject paths outside an existing project root.

    Both relative and absolute requested paths are supported. Symbolic links
    are resolved before the boundary comparison. Missing paths are rejected:
    this policy is for reading existing files, not for creating new ones.
    """
    root = project_root.resolve(strict=True)
    if not root.is_dir():
        raise ProjectPathDenied("The authorized project root is not a directory.")

    candidate = requested_path if requested_path.is_absolute() else root / requested_path
    try:
        resolved_candidate = candidate.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ProjectPathDenied("The requested path could not be resolved.") from error

    if not resolved_candidate.is_relative_to(root):
        raise ProjectPathDenied("The requested path escapes the authorized project root.")
    return resolved_candidate
