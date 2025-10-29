"""Helpers for dealing with user-provided filesystem paths."""
from __future__ import annotations

import os
import re
from pathlib import Path, PureWindowsPath
from typing import overload

_WINDOWS_DRIVE_RE = re.compile(r"^[a-zA-Z]:([/\\]|$)")


def _to_string(value: Path | os.PathLike[str] | str) -> str:
    """Coerce *value* to a plain string."""

    return os.fspath(value)


def _is_windows_path(text: str) -> bool:
    """Return ``True`` if *text* looks like a Windows absolute path."""

    return bool(_WINDOWS_DRIVE_RE.match(text) or text.startswith("\\\\"))


@overload
def normalize_user_path(value: None) -> None: ...


@overload
def normalize_user_path(value: Path | os.PathLike[str] | str) -> str: ...


def normalize_user_path(
    value: Path | os.PathLike[str] | str | None,
) -> str | None:
    """Normalize a path entered by a user.

    The function performs a couple of safety tweaks that help the application
    behave consistently across operating systems:

    * trims whitespace and surrounding quotes (useful when paths are copied
      from documentation);
    * expands the user home directory (``~``);
    * normalises path separators, taking special care of Windows drive/UNC
      prefixes even when the code is executed on a non-Windows platform.
    """

    if value is None:
        return None

    text = _to_string(value)
    text = text.strip()
    if not text:
        return None

    if text.startswith('"') and text.endswith('"') and len(text) > 1:
        text = text[1:-1]

    text = os.path.expanduser(text)

    if _is_windows_path(text):
        return str(PureWindowsPath(text))

    return os.path.normpath(text)


def format_for_display(path: Path | os.PathLike[str] | str | None) -> str:
    """Return a human-friendly representation of *path*.

    ``format_for_display`` reuses :func:`normalize_user_path` to guarantee that
    Windows paths are rendered with backslashes while POSIX paths use forward
    slashes. Empty values are converted to an empty string.
    """

    normalized = normalize_user_path(path)
    if normalized is None:
        return ""
    return normalized


def format_for_logging(path: Path | os.PathLike[str] | str | None) -> str:
    """Return an escaped representation of *path* suitable for logs."""

    normalized = normalize_user_path(path)
    if normalized is None:
        return "\"\""

    escaped = normalized.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


__all__ = ["format_for_display", "format_for_logging", "normalize_user_path"]
