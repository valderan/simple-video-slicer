"""Вспомогательные функции для валидации."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from .time_parser import parse_time

SUPPORTED_INPUT_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mkv",
    ".webm",
    ".mov",
    ".flv",
    ".wmv",
    ".mpg",
    ".mpeg",
    ".m4v",
    ".3gp",
}

SUPPORTED_OUTPUT_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".avi",
    ".webm",
    ".mov",
}


def ensure_ffmpeg_available() -> None:
    """Проверяет доступность ffmpeg в PATH."""
    if not shutil.which("ffmpeg"):
        raise FileNotFoundError(
            "FFmpeg не найден. Установите ffmpeg и добавьте его в PATH."
        )


def validate_input_file(path: str | os.PathLike[str]) -> Path:
    """Проверяет существование входного файла и поддерживаемое расширение."""
    candidate = Path(path).expanduser().resolve()
    if not candidate.exists():
        raise FileNotFoundError(f"Файл не найден: {candidate}")
    if not candidate.is_file():
        raise ValueError(f"Указан не файл: {candidate}")
    if candidate.suffix.lower() not in SUPPORTED_INPUT_EXTENSIONS:
        raise ValueError(
            f"Неподдерживаемое расширение файла: {candidate.suffix}. "
            f"Поддерживаемые форматы: {', '.join(sorted(SUPPORTED_INPUT_EXTENSIONS))}"
        )
    return candidate


def validate_output_dir(path: str | os.PathLike[str]) -> Path:
    """Проверяет существование и доступность выходной директории."""
    directory = Path(path).expanduser().resolve()
    if not directory.exists():
        raise FileNotFoundError(f"Каталог не найден: {directory}")
    if not directory.is_dir():
        raise ValueError(f"Указан не каталог: {directory}")
    if not os.access(directory, os.W_OK):
        raise PermissionError(f"Недостаточно прав для записи в каталог: {directory}")
    return directory


def parse_table_time(value: str) -> float:
    """Проксирует парсинг времени с обработкой ошибок."""
    try:
        return parse_time(value)
    except ValueError as exc:
        raise ValueError(f"Некорректное время: {value}") from exc
