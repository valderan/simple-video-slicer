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
    container: str = "mp4"
    convert: bool = False
    video_codec: str = "copy"
    audio_codec: str = "copy"
    crf: int = 23
    extra_args: str = ""
    remove_audio: bool = False
    index: int = field(default=0)

    def duration(self) -> Optional[float]:
        if self.end is None:
            return None
        return max(0.0, self.end - self.start)

    def output_path(self, output_dir: Path, default_ext: str) -> Path:
        if self.filename:
            filename = self.filename
            if "." not in Path(filename).name:
                filename = f"{filename}.{self.container or default_ext.lstrip('.')}"
        else:
            extension = self.container or default_ext.lstrip(".")
            if not extension.startswith("."):
                extension = f".{extension}"
            filename = f"segment_{self.index:03d}{extension}"
        return output_dir / filename
