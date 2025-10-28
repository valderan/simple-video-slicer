"""Модель данных для сегмента видео."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class Segment:
    """Описание одного фрагмента видео."""

    start: float
    end: Optional[float] = None
    filename: Optional[str] = None
    video_codec: str = "copy"
    audio_codec: str = "copy"
    crf: int = 23
    extra_args: str = ""
    index: int = field(default=0)

    def duration(self) -> Optional[float]:
        if self.end is None:
            return None
        return max(0.0, self.end - self.start)

    def output_path(self, output_dir: Path, default_ext: str) -> Path:
        name = self.filename or f"segment_{self.index:03d}{default_ext}"
        return output_dir / name
