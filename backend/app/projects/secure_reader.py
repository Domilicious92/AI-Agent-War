"""Read-only project access using descriptor-relative filesystem operations.

Linux/POSIX only. The root directory is opened with O_DIRECTORY and O_NOFOLLOW;
each relative component is opened relative to its parent descriptor. This avoids
the path-resolution TOCTOU window of a standalone pathlib check. The caller must
still authorize the project root, isolate the worker and enforce resource limits.
"""

import os
from pathlib import Path, PurePosixPath


class ProjectReadDenied(ValueError):
    """A read was denied by the project boundary policy."""


def read_project_file(project_root: Path, relative_path: str, max_bytes: int = 1_048_576) -> bytes:
    """Read a regular file within the root without following symbolic links.

    Reject absolute paths, traversal, symlinks, special files and oversized
    content. File descriptors are always closed, including on failure.
    """
    if os.name != "posix" or not hasattr(os, "O_NOFOLLOW"):
        raise ProjectReadDenied("Secure project reads require POSIX O_NOFOLLOW.")
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes < 0:
        raise ProjectReadDenied("The byte limit must be a nonnegative integer.")
    if not isinstance(relative_path, str) or not relative_path:
        raise ProjectReadDenied("A nonempty relative path is required.")

    requested_path = PurePosixPath(relative_path)
    components = relative_path.split("/")
    if (
        requested_path.is_absolute()
        or any(component in ("", ".", "..") for component in components)
        or "\\\" in relative_path
        or "\x00" in relative_path
    ):
        raise ProjectReadDenied("Unsafe project-relative path.")

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
    descriptors: list[int] = []
    try:
        root_descriptor = os.open(project_root, directory_flags)
        descriptors.append(root_descriptor)
        for component in components[:-1]:
            child_descriptor = os.open(component, directory_flags, dir_fd=descriptors[-1])
            descriptors.append(child_descriptor)
        file_descriptor = os.open(components[-1], file_flags, dir_fd=descriptors[-1])
        descriptors.append(file_descriptor)
        import stat

        metadata = os.fstat(file_descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ProjectReadDenied("Only regular files may be read.")
        if metadata.st_size > max_bytes:
            raise ProjectReadDenied("The file exceeds the allowed size.")
        with os.fdopen(os.dup(file_descriptor), "rb") as file_stream:
            contents = file_stream.read(max_bytes + 1)
        if len(contents) > max_bytes:
            raise ProjectReadDenied("The file exceeds the allowed size.")
        return contents
    except (OSError, OverflowError) as error:
        raise ProjectReadDenied("Secure project read failed.") from error
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
