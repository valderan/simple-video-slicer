"""Утилиты для взаимодействия с ffmpeg."""
from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Iterable, List

from .time_parser import format_time

logger = logging.getLogger(__name__)


def run_ffmpeg(args: Iterable[str]) -> subprocess.CompletedProcess[str]:
    """Запускает ffmpeg с заданными аргументами и возвращает результат."""
    command = ["ffmpeg", "-y", *args]
    logger.debug("Запуск команды FFmpeg: %s", " ".join(command))
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        logger.error("FFmpeg завершился с ошибкой: %s", result.stderr)
        raise RuntimeError(result.stderr.strip())
    return result


def probe_file(path: Path) -> dict:
    """Получает информацию о видеофайле с помощью ffprobe."""
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        "-print_format",
        "json",
        str(path),
    ]
    logger.debug("Запуск команды ffprobe: %s", " ".join(command))
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        logger.error("ffprobe завершился с ошибкой: %s", result.stderr)
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout)


def generate_thumbnail(input_file: Path, timestamp: float, output_file: Path) -> Path:
    """Создаёт изображение предпросмотра для указанного времени."""
    output_file = output_file.with_suffix(".jpg")
    args: List[str] = [
        "-ss",
        str(timestamp),
        "-i",
        str(input_file),
        "-frames:v",
        "1",
        str(output_file),
    ]
    run_ffmpeg(args)
    return output_file


def format_seconds(value: float) -> str:
    """Форматирует секунды в строку для передачи в FFmpeg."""
    return format_time(value).rstrip("0").rstrip(".")
