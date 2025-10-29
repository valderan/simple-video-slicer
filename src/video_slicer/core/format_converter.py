"""Конвертация видеоформатов."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from ..utils import ffmpeg_helper, path_utils

logger = logging.getLogger(__name__)


class FormatConverter:
    """Простая обёртка для изменения контейнера или кодеков."""

    def convert(
        self,
        input_file: Path,
        output_file: Path,
        video_codec: str = "copy",
        audio_codec: str = "copy",
        extra_args: Iterable[str] | None = None,
    ) -> Path:
        args = ["-i", str(input_file), "-c:v", video_codec, "-c:a", audio_codec]
        if extra_args:
            args.extend(extra_args)
        args.append(str(output_file))
        logger.info(
            "Начата конвертация %s -> %s",
            path_utils.format_for_logging(input_file),
            path_utils.format_for_logging(output_file),
        )
        ffmpeg_helper.run_ffmpeg(args)
        logger.info("Конвертация завершена успешно")
        return output_file
