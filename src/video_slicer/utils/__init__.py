"""Utility package exports and backward-compatibility helpers."""
from __future__ import annotations

import os
from importlib import import_module
from pathlib import Path

ffmpeg_helper = import_module(".ffmpeg_helper", __name__)
path_utils = import_module(".path_utils", __name__)
validators = import_module(".validators", __name__)

__all__ = ["ffmpeg_helper", "path_utils", "validators"]


def _ensure_logging_formatter() -> None:
    """Backfill :func:`path_utils.format_for_logging` when missing."""

    if hasattr(path_utils, "format_for_logging"):
        return

    def _format_for_logging(path: Path | os.PathLike[str] | str | None) -> str:
        normalized = path_utils.normalize_user_path(path)
        if normalized is None:
            return '""'
        escaped = normalized.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    path_utils.format_for_logging = _format_for_logging  # type: ignore[attr-defined]


_ensure_logging_formatter()
