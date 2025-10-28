"""Утилиты для работы со временем."""
from __future__ import annotations

import re
from typing import Tuple

_TIME_RE = re.compile(
    r"^(?:(\d{1,2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?|"  # HH:MM:SS(.mmm)
    r"(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?|"               # MM:SS(.mmm)
    r"(\d+)(?:\.(\d{1,3}))?)$"                           # SS(.mmm)
)


def parse_time(value: str) -> float:
    """Парсит строковое значение времени в секунды.

    Поддерживаются форматы HH:MM:SS(.mmm), MM:SS(.mmm) и SS(.mmm).
    """
    value = value.strip()
    if not value:
        raise ValueError("Пустое значение времени")

    match = _TIME_RE.match(value)
    if not match:
        raise ValueError(f"Некорректный формат времени: {value}")

    groups: Tuple[str | None, ...] = match.groups()
    hours = minutes = seconds = millis = 0

    if groups[0] is not None:
        hours = int(groups[0])
        minutes = int(groups[1])
        seconds = int(groups[2])
        if groups[3] is not None:
            millis = int(groups[3].ljust(3, "0"))
    elif groups[4] is not None:
        minutes = int(groups[4])
        seconds = int(groups[5])
        if groups[6] is not None:
            millis = int(groups[6].ljust(3, "0"))
    else:
        seconds = int(groups[7])
        if groups[8] is not None:
            millis = int(groups[8].ljust(3, "0"))

    total_seconds = hours * 3600 + minutes * 60 + seconds + millis / 1000
    return total_seconds


def format_time(seconds: float) -> str:
    """Форматирует значение секунд в строку HH:MM:SS.mmm."""
    if seconds < 0:
        raise ValueError("Время не может быть отрицательным")

    total_millis = int(round(seconds * 1000))
    millis = total_millis % 1000
    total_seconds = total_millis // 1000
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h:02d}:{m:02d}:{s:02d}.{millis:03d}"
