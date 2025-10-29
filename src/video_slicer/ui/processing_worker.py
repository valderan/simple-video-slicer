"""Helpers for running long operations in background threads."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PySide6 import QtCore

from ..core.video_processor import VideoProcessor
from ..models.segment import Segment
from ..utils import path_utils
from ..utils.settings import AppSettings


class ProcessingWorker(QtCore.QObject):
    """Execute video processing in a worker thread.

    The worker emits simple signals that the UI can convert into
    user-facing messages in the appropriate language.
    """

    segment_started = QtCore.Signal(int, int, str)
    segment_finished = QtCore.Signal(int, int, str)
    progress_changed = QtCore.Signal(int)
    error_occurred = QtCore.Signal(str)
    finished = QtCore.Signal()
    stopped = QtCore.Signal()

    def __init__(
        self,
        input_file: Path,
        output_dir: Path,
        segments: Iterable[Segment],
        settings: AppSettings,
    ) -> None:
        super().__init__()
        self._input_file = input_file
        self._output_dir = output_dir
        self._segments = list(segments)
        self._stop_requested = False
        self._settings = settings.clone()

    @QtCore.Slot()
    def run(self) -> None:
        processor = VideoProcessor(
            self._input_file,
            self._output_dir,
            settings=self._settings,
        )
        total = len(self._segments)
        if total == 0:
            self.finished.emit()
            return

        for index, segment in enumerate(self._segments, start=1):
            if self._stop_requested:
                self.stopped.emit()
                return

            container = segment.container or self._input_file.suffix.lstrip(".") or "mp4"
            if segment.filename:
                display_name = path_utils.format_for_display(segment.filename)
            else:
                display_name = f"segment_{segment.index:03d}.{container}"
            self.segment_started.emit(index, total, display_name)

            try:
                processor.process_segment(segment)
            except Exception as exc:  # noqa: BLE001
                self.error_occurred.emit(str(exc))
                return

            percent = int(index / total * 100)
            self.progress_changed.emit(percent)
            self.segment_finished.emit(index, total, display_name)

        self.finished.emit()

    def request_stop(self) -> None:
        self._stop_requested = True
