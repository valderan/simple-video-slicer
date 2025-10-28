"""Управление списком сегментов."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ..models.segment import Segment


@dataclass
class SegmentManager:
    """Коллекция сегментов с базовыми операциями."""

    segments: List[Segment] = field(default_factory=list)

    def add_segment(self, segment: Segment) -> None:
        segment.index = len(self.segments) + 1
        self.segments.append(segment)

    def remove_segment(self, index: int) -> None:
        if 0 <= index < len(self.segments):
            del self.segments[index]
            self._reindex()

    def clear(self) -> None:
        self.segments.clear()

    def get(self, index: int) -> Optional[Segment]:
        if 0 <= index < len(self.segments):
            return self.segments[index]
        return None

    def _reindex(self) -> None:
        for idx, segment in enumerate(self.segments, start=1):
            segment.index = idx
