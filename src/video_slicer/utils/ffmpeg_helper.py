"""Утилиты для взаимодействия с ffmpeg."""
from __future__ import annotations

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List, Sequence

from .time_parser import format_time

logger = logging.getLogger(__name__)

_ffmpeg_command: Sequence[str] = ("ffmpeg",)
_ffprobe_command: Sequence[str] = ("ffprobe",)


def set_ffmpeg_paths(ffmpeg: str | None, ffprobe: str | None = None) -> None:
    """Configure explicit paths for ffmpeg/ffprobe commands."""

    global _ffmpeg_command, _ffprobe_command
    _ffmpeg_command = (ffmpeg,) if ffmpeg else ("ffmpeg",)
    if ffprobe:
        _ffprobe_command = (ffprobe,)
    elif ffmpeg and ffmpeg.endswith("ffmpeg"):
        # Try to derive ffprobe from ffmpeg folder
        probe_candidate = str(Path(ffmpeg).with_name("ffprobe"))
        _ffprobe_command = (probe_candidate,)
    else:
        _ffprobe_command = ("ffprobe",)


def current_ffmpeg() -> str:
    return _ffmpeg_command[0]


def ensure_ffmpeg_available() -> None:
    """Ensure that the configured ffmpeg binary is present."""

    command = current_ffmpeg()
    if shutil.which(command) or Path(command).exists():
        return
    raise FileNotFoundError(
        "FFmpeg не найден. Укажите путь к ffmpeg в настройках или добавьте его в PATH."
    )


def run_ffmpeg(args: Iterable[str]) -> subprocess.CompletedProcess[str]:
    """Запускает ffmpeg с заданными аргументами и возвращает результат."""
    ensure_ffmpeg_available()
    command = [*_ffmpeg_command, "-y", *args]
    logger.debug("Запуск команды FFmpeg: %s", " ".join(command))
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        logger.error("FFmpeg завершился с ошибкой: %s", result.stderr)
        raise RuntimeError(result.stderr.strip())
    return result


def probe_file(path: Path) -> dict:
    """Получает информацию о видеофайле с помощью ffprobe."""
    command = [
        *_ffprobe_command,
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
        encoding="utf-8",
        errors="replace",
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
