"""Диалог предпросмотра сегмента."""
from __future__ import annotations

import logging
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from ..utils import ffmpeg_helper
from ..utils.time_parser import format_time
from .translations import Translator

logger = logging.getLogger(__name__)


class PreviewDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        translator: Translator,
        input_file: Path,
        start: float,
    ) -> None:
        super().__init__(parent)
        self.translator = translator
        self.input_file = input_file
        self.start = start
        self._thumbnail_path: Path | None = None
        self.setWindowTitle(self.translator.tr("preview_title"))
        self.setModal(True)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.info_label = QtWidgets.QLabel()
        self.close_button = QtWidgets.QPushButton(self.translator.tr("preview_close"))
        self.close_button.clicked.connect(self.accept)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.image_label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.close_button)

        self._generate_preview()

    def _generate_preview(self) -> None:
        try:
            tmp_file = Path(QtCore.QStandardPaths.writableLocation(
                QtCore.QStandardPaths.StandardLocation.TempLocation
            )) / "svs_preview.jpg"
            tmp_file.parent.mkdir(parents=True, exist_ok=True)
            self._thumbnail_path = ffmpeg_helper.generate_thumbnail(
                self.input_file, self.start, tmp_file
            )
            pixmap = QtGui.QPixmap(str(self._thumbnail_path))
            if pixmap.isNull():
                raise RuntimeError("Не удалось загрузить изображение")
            self.image_label.setPixmap(pixmap.scaled(
                480,
                270,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            ))
            formatted_time = format_time(self.start).split(".")[0]
            self.info_label.setText(
                f"{self.translator.tr('start_time')}: {formatted_time}"
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Ошибка при генерации предпросмотра")
            self.info_label.setText(str(exc))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # noqa: N802
        if self._thumbnail_path and self._thumbnail_path.exists():
            try:
                self._thumbnail_path.unlink()
            except OSError:
                logger.debug("Не удалось удалить временный файл")
        super().closeEvent(event)
