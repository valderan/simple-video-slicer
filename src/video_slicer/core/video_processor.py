"""Логика нарезки видео с помощью FFmpeg."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, List

from ..models.segment import Segment
from ..utils import ffmpeg_helper

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Обёртка над FFmpeg для нарезки видео на сегменты."""

    def __init__(self, input_file: Path, output_dir: Path) -> None:
        self.input_file = input_file
        self.output_dir = output_dir

    def slice_segments(self, segments: Iterable[Segment]) -> None:
        for segment in segments:
            self.process_segment(segment)

    def process_segment(self, segment: Segment) -> None:
        output_path = segment.output_path(
            self.output_dir, default_ext=self.input_file.suffix
        )
        args: List[str] = [
            "-ss",
            ffmpeg_helper.format_seconds(segment.start),
        ]
        if segment.end is not None:
            duration = segment.end - segment.start
            args.extend(["-t", ffmpeg_helper.format_seconds(duration)])
        args.extend(["-i", str(self.input_file)])

        video_codec = segment.video_codec or "copy"
        audio_codec = segment.audio_codec or "copy"
        args.extend(["-c:v", video_codec])
        args.extend(["-c:a", audio_codec])
        if segment.convert and video_codec != "copy":
            args.extend(["-crf", str(segment.crf)])
        if segment.convert and segment.extra_args:
            args.extend(segment.extra_args.split())
        args.append(str(output_path))

        logger.info("Начата обработка сегмента %s", segment.index)
        ffmpeg_helper.run_ffmpeg(args)
        logger.info("Сегмент %s успешно сохранён в %s", segment.index, output_path)
