"""Главное окно приложения."""
from __future__ import annotations

import logging
from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from ..core.segment_manager import SegmentManager
from ..core.video_processor import VideoProcessor
from ..models.segment import Segment
from ..utils import ffmpeg_helper, validators
from ..utils.time_parser import format_time
from .preview_dialog import PreviewDialog
from .segment_dialog import SegmentDialog
from .translations import Translator

logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.translator = Translator("ru")
        self.segment_manager = SegmentManager()
        self.input_file: Path | None = None
        self.output_dir: Path | None = None
        self._file_info: dict[str, object] | None = None
        self._stop_requested = False

        self.setWindowTitle("SVS - Simple Video Slicer")
        self.resize(900, 600)

        self._create_actions()
        self._create_menu()
        self._create_widgets()
        self._create_status_bar()
        self.retranslate_ui()

    def _create_actions(self) -> None:
        self.help_action = QtGui.QAction()
        self.help_action.triggered.connect(self.show_help)

        self.lang_ru_action = QtGui.QAction(checkable=True)
        self.lang_ru_action.triggered.connect(lambda: self.set_language("ru"))
        self.lang_en_action = QtGui.QAction(checkable=True)
        self.lang_en_action.triggered.connect(lambda: self.set_language("en"))

    def _create_menu(self) -> None:
        menubar = self.menuBar()
        self.help_menu = menubar.addMenu("")
        self.help_menu.addAction(self.help_action)

        self.language_menu = menubar.addMenu("")
        language_group = QtGui.QActionGroup(self)
        language_group.addAction(self.lang_ru_action)
        language_group.addAction(self.lang_en_action)
        self.language_menu.addAction(self.lang_ru_action)
        self.language_menu.addAction(self.lang_en_action)
        self.lang_ru_action.setChecked(True)

    def _create_widgets(self) -> None:
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        file_layout = QtWidgets.QHBoxLayout()
        self.file_label = QtWidgets.QLabel()
        self.file_line = QtWidgets.QLineEdit()
        self.file_line.setReadOnly(True)
        self.file_button = QtWidgets.QPushButton()
        self.file_button.clicked.connect(self.select_input_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_line)
        file_layout.addWidget(self.file_button)

        self.file_info_label = QtWidgets.QLabel()
        self.file_info_label.setStyleSheet("color: #00c853;")

        output_layout = QtWidgets.QHBoxLayout()
        self.output_label = QtWidgets.QLabel()
        self.output_line = QtWidgets.QLineEdit()
        self.output_line.setReadOnly(True)
        self.output_button = QtWidgets.QPushButton()
        self.output_button.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.output_button)

        self.table = QtWidgets.QTableWidget(0, 7)
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        for column in range(2, 6):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.itemDoubleClicked.connect(self.edit_segment)

        button_layout = QtWidgets.QHBoxLayout()
        self.add_button = QtWidgets.QPushButton()
        self.add_button.clicked.connect(self.add_segment)
        self.edit_button = QtWidgets.QPushButton()
        self.edit_button.clicked.connect(self.edit_segment)
        self.remove_button = QtWidgets.QPushButton()
        self.remove_button.clicked.connect(self.remove_segment)
        self.duplicate_button = QtWidgets.QPushButton()
        self.duplicate_button.clicked.connect(self.duplicate_segment)
        self.preview_button = QtWidgets.QPushButton()
        self.preview_button.clicked.connect(self.preview_segment)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.duplicate_button)
        button_layout.addWidget(self.preview_button)
        button_layout.addStretch()

        self.progress_info_label = QtWidgets.QLabel()
        self.progress_label = QtWidgets.QLabel()
        progress_header_layout = QtWidgets.QHBoxLayout()
        progress_header_layout.addWidget(self.progress_label)
        progress_header_layout.addWidget(self.progress_info_label)
        progress_header_layout.addStretch()
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.log_label = QtWidgets.QLabel()
        self.log_console = QtWidgets.QPlainTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumBlockCount(500)

        self.process_button = QtWidgets.QPushButton()
        self.process_button.clicked.connect(self.process_segments)
        self.stop_button = QtWidgets.QPushButton()
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)

        process_buttons_layout = QtWidgets.QHBoxLayout()
        process_buttons_layout.addWidget(self.process_button)
        process_buttons_layout.addWidget(self.stop_button)
        process_buttons_layout.addStretch()

        layout.addLayout(file_layout)
        layout.addWidget(self.file_info_label)
        layout.addLayout(output_layout)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        layout.addLayout(progress_header_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_label)
        layout.addWidget(self.log_console)
        layout.addLayout(process_buttons_layout)

        self.setCentralWidget(central)

    def _create_status_bar(self) -> None:
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

    def retranslate_ui(self) -> None:
        self.file_label.setText(self.translator.tr("file_label"))
        self.file_button.setText(self.translator.tr("browse"))
        self.output_label.setText(self.translator.tr("output_label"))
        self.output_button.setText(self.translator.tr("browse"))
        self.file_button.setToolTip(self.translator.tr("tooltip_file"))
        self.output_button.setToolTip(self.translator.tr("tooltip_output"))
        self.add_button.setText(self.translator.tr("add_segment"))
        self.add_button.setToolTip(self.translator.tr("tooltip_add"))
        self.edit_button.setText(self.translator.tr("edit_segment"))
        self.edit_button.setToolTip(self.translator.tr("tooltip_edit"))
        self.remove_button.setText(self.translator.tr("remove_segment"))
        self.remove_button.setToolTip(self.translator.tr("tooltip_remove"))
        self.duplicate_button.setText(self.translator.tr("duplicate_segment"))
        self.duplicate_button.setToolTip(self.translator.tr("tooltip_duplicate"))
        self.preview_button.setText(self.translator.tr("preview"))
        self.preview_button.setToolTip(self.translator.tr("tooltip_preview"))
        self.process_button.setText(self.translator.tr("process"))
        self.process_button.setToolTip(self.translator.tr("tooltip_process"))
        self.stop_button.setText(self.translator.tr("stop"))
        self.stop_button.setToolTip(self.translator.tr("tooltip_stop"))
        self.file_line.setToolTip(self.file_line.text())
        self.output_line.setToolTip(self.output_line.text())
        self.table.setToolTip(self.translator.tr("segment_table"))
        self.progress_label.setText(self.translator.tr("progress_label"))
        self.progress_info_label.setText(self.translator.tr("progress_idle"))
        self.log_label.setText(self.translator.tr("log_label"))
        self.help_menu.setTitle(self.translator.tr("help_menu"))
        self.help_action.setText(self.translator.tr("help_manual"))
        self.language_menu.setTitle(self.translator.tr("language_menu"))
        self.lang_ru_action.setText(self.translator.tr("language_ru"))
        self.lang_en_action.setText(self.translator.tr("language_en"))
        self.status_bar.showMessage(self.translator.tr("status_ready"))
        self._update_table_headers()
        if self._file_info:
            self.file_info_label.setText(self._format_file_info(self._file_info))

    def _update_table_headers(self) -> None:
        headers = [
            "#",
            self.translator.tr("filename"),
            self.translator.tr("start_time"),
            self.translator.tr("end_time"),
            self.translator.tr("format"),
            self.translator.tr("convert_column"),
            self.translator.tr("preview"),
        ]
        for idx, text in enumerate(headers):
            item = self.table.horizontalHeaderItem(idx)
            if item:
                item.setText(text)
            else:
                self.table.setHorizontalHeaderItem(idx, QtWidgets.QTableWidgetItem(text))

    def set_language(self, language: str) -> None:
        self.translator.set_language(language)
        self.lang_ru_action.setChecked(language == "ru")
        self.lang_en_action.setChecked(language == "en")
        self.retranslate_ui()

    def show_help(self) -> None:
        QtWidgets.QMessageBox.information(
            self,
            self.translator.tr("help_manual"),
            "SVS - Simple Video Slicer\n\n"
            "1. Выберите входной файл и выходную папку.\n"
            "2. Добавьте сегменты, указав начало и конец.\n"
            "3. Нажмите 'Запустить обработку' для запуска FFmpeg.",
        )

    def select_input_file(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.translator.tr("file_label"),
            str(Path.home()),
            "Video Files (*.mp4 *.avi *.mkv *.webm *.mov *.flv *.wmv *.mpg *.mpeg *.m4v *.3gp)",
        )
        if file_path:
            try:
                validators.validate_input_file(file_path)
                self.input_file = Path(file_path)
                self.file_line.setText(file_path)
                logger.info("Выбран входной файл: %s", file_path)
                info = self._probe_file(self.input_file)
                self._file_info = info
                self.file_info_label.setText(self._format_file_info(info))
            except Exception as exc:  # noqa: BLE001
                QtWidgets.QMessageBox.critical(
                    self, self.translator.tr("error"), str(exc)
                )
                self._file_info = None
                self.file_info_label.setText(str(exc))

    def select_output_dir(self) -> None:
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            self.translator.tr("output_label"),
            str(Path.home()),
        )
        if directory:
            try:
                self.output_dir = validators.validate_output_dir(directory)
                self.output_line.setText(str(self.output_dir))
                logger.info("Выходная директория: %s", self.output_dir)
            except Exception as exc:  # noqa: BLE001
                QtWidgets.QMessageBox.critical(
                    self, self.translator.tr("error"), str(exc)
                )

    def add_segment(self) -> None:
        dialog = SegmentDialog(self, self.translator)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            try:
                segment = dialog.get_segment()
                self.segment_manager.add_segment(segment)
                logger.info(
                    "Добавлен сегмент #%s (%s-%s)",
                    segment.index,
                    format_time(segment.start),
                    "" if segment.end is None else format_time(segment.end),
                )
                self._refresh_table()
            except Exception as exc:  # noqa: BLE001
                QtWidgets.QMessageBox.critical(
                    self, self.translator.tr("error"), str(exc)
                )

    def remove_segment(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.segment_manager.remove_segment(row)
            logger.info("Удалён сегмент #%s", row + 1)
            self._refresh_table()

    def edit_segment(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        segment = self.segment_manager.get(row)
        if not segment:
            return
        dialog = SegmentDialog(self, self.translator, segment)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            try:
                updated = dialog.get_segment()
                updated.index = segment.index
                self.segment_manager.update_segment(row, updated)
                logger.info("Обновлён сегмент #%s", updated.index)
                self._refresh_table()
            except Exception as exc:  # noqa: BLE001
                QtWidgets.QMessageBox.critical(
                    self, self.translator.tr("error"), str(exc)
                )

    def duplicate_segment(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        segment = self.segment_manager.get(row)
        if not segment:
            return
        duplicate = replace(segment)
        duplicate.index = 0
        self.segment_manager.insert_segment(row + 1, duplicate)
        logger.info("Дублирован сегмент #%s", row + 1)
        self._refresh_table()

    def preview_segment(self) -> None:
        if not self.input_file:
            return
        row = self.table.currentRow()
        if row < 0:
            return
        self._show_preview_for_row(row)

    def _show_preview_for_row(self, row: int) -> None:
        segment = self.segment_manager.get(row)
        if not segment:
            return
        dialog = PreviewDialog(self, self.translator, self.input_file, segment.start)
        dialog.exec()

    def _refresh_table(self) -> None:
        self.table.setRowCount(len(self.segment_manager.segments))
        preview_text = self.translator.tr("preview_icon")
        default_container = "mp4"
        if self.input_file and self.input_file.suffix:
            default_container = self.input_file.suffix.lstrip(".") or default_container
        for row, segment in enumerate(self.segment_manager.segments):
            items = [
                QtWidgets.QTableWidgetItem(str(segment.index)),
                QtWidgets.QTableWidgetItem(segment.filename or ""),
                QtWidgets.QTableWidgetItem(format_time(segment.start)),
                QtWidgets.QTableWidgetItem(
                    "" if segment.end is None else format_time(segment.end)
                ),
                QtWidgets.QTableWidgetItem(segment.container or default_container),
                QtWidgets.QTableWidgetItem(
                    self.translator.tr("yes")
                    if segment.convert
                    else self.translator.tr("no")
                ),
            ]
            for col, item in enumerate(items):
                if col == 0:
                    item.setFlags(
                        QtCore.Qt.ItemFlag.ItemIsSelectable
                        | QtCore.Qt.ItemFlag.ItemIsEnabled
                    )
                else:
                    item.setFlags(
                        QtCore.Qt.ItemFlag.ItemIsSelectable
                        | QtCore.Qt.ItemFlag.ItemIsEnabled
                    )
                self.table.setItem(row, col, item)
            preview_button = QtWidgets.QPushButton(preview_text)
            preview_button.clicked.connect(partial(self._show_preview_for_row, row))
            self.table.setCellWidget(row, 6, preview_button)

    def _collect_segments_from_table(self) -> List[Segment]:
        return [replace(segment) for segment in self.segment_manager.segments]

    def process_segments(self) -> None:
        if not self.input_file:
            QtWidgets.QMessageBox.warning(
                self, self.translator.tr("error"), "Не выбран входной файл"
            )
            return
        if not self.output_dir:
            QtWidgets.QMessageBox.warning(
                self, self.translator.tr("error"), "Не выбрана выходная папка"
            )
            return
        if not self.segment_manager.segments:
            QtWidgets.QMessageBox.information(
                self, self.translator.tr("info"), self.translator.tr("no_segments")
            )
            return
        try:
            validators.ensure_ffmpeg_available()
        except Exception as exc:  # noqa: BLE001
            QtWidgets.QMessageBox.critical(
                self, self.translator.tr("error"), str(exc)
            )
            return

        segments = self._collect_segments_from_table()
        total = len(segments)
        if total == 0:
            QtWidgets.QMessageBox.information(
                self, self.translator.tr("info"), self.translator.tr("no_segments")
            )
            return

        processor = VideoProcessor(self.input_file, self.output_dir)
        self._stop_requested = False
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_info_label.setText(
            self.translator.tr("progress_template").format(current=0, total=total)
        )
        self.status_bar.showMessage(self.translator.tr("status_processing"))
        self.log_console.clear()

        was_stopped = False
        for index, segment in enumerate(segments, start=1):
            QtWidgets.QApplication.processEvents()
            if self._stop_requested:
                self._append_log(self.translator.tr("processing_stop_ack"))
                was_stopped = True
                break

            container = segment.container or "mp4"
            display_name = segment.filename or f"segment_{segment.index:03d}.{container}"
            self.progress_info_label.setText(
                self.translator.tr("progress_template").format(
                    current=index, total=total
                )
            )
            self.status_bar.showMessage(
                self.translator.tr("status_processing_segment").format(
                    current=index, total=total, name=display_name
                )
            )
            self._append_log(
                self.translator.tr("log_processing_segment").format(
                    current=index, total=total, name=display_name
                )
            )

            try:
                processor.process_segment(segment)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Ошибка при обработке сегментов")
                self._append_log(str(exc))
                QtWidgets.QMessageBox.critical(
                    self, self.translator.tr("error"), str(exc)
                )
                break

            self.progress_bar.setValue(int(index / total * 100))
            self._append_log(
                self.translator.tr("log_segment_done").format(name=display_name)
            )

        else:
            self._append_log(self.translator.tr("processing_complete"))
            QtWidgets.QMessageBox.information(
                self,
                self.translator.tr("info"),
                self.translator.tr("processing_complete"),
            )

        if was_stopped or self._stop_requested:
            self.status_bar.showMessage(self.translator.tr("status_stopped"))
            self.progress_info_label.setText(self.translator.tr("progress_idle"))
            self.progress_bar.setValue(0)
        else:
            self.status_bar.showMessage(self.translator.tr("status_ready"))
        self.process_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._stop_requested = False

    def stop_processing(self) -> None:
        if not self.stop_button.isEnabled():
            return
        self._stop_requested = True
        self.stop_button.setEnabled(False)
        self._append_log(self.translator.tr("processing_stop_requested"))

    def _append_log(self, message: str) -> None:
        timestamp = QtCore.QDateTime.currentDateTime().toString("HH:mm:ss")
        self.log_console.appendPlainText(f"[{timestamp}] {message}")

    def _probe_file(self, path: Path) -> dict[str, object]:
        try:
            data = ffmpeg_helper.probe_file(path)
        except Exception:
            logger.exception("Не удалось получить информацию о файле")
            raise

        duration_raw = data.get("format", {}).get("duration")
        streams = data.get("streams", [])
        video_streams = [s for s in streams if s.get("codec_type") == "video"]
        audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
        video_info = video_streams[0] if video_streams else {}
        audio_info = audio_streams[0] if audio_streams else {}
        duration_value = float(duration_raw) if duration_raw else None
        width_raw = video_info.get("width")
        height_raw = video_info.get("height")
        width = self._safe_int(width_raw)
        height = self._safe_int(height_raw)
        info: dict[str, object] = {
            "duration": duration_value,
            "resolution": (width, height) if width and height else None,
            "video_codec": video_info.get("codec_name"),
            "audio_codec": audio_info.get("codec_name"),
        }
        return info

    def _format_file_info(self, info: dict[str, object]) -> str:
        duration_value = info.get("duration")
        if isinstance(duration_value, (int, float)) and duration_value >= 0:
            duration_text = self._format_duration(duration_value)
        else:
            duration_text = self.translator.tr("file_info_unknown")

        resolution_value = info.get("resolution")
        if (
            isinstance(resolution_value, tuple)
            and len(resolution_value) == 2
            and all(isinstance(v, int) and v > 0 for v in resolution_value)
        ):
            resolution_text = f"{resolution_value[0]}x{resolution_value[1]}"
        else:
            resolution_text = self.translator.tr("file_info_unknown")

        codecs = []
        for key in ("video_codec", "audio_codec"):
            value = info.get(key)
            if isinstance(value, str) and value:
                codecs.append(value.upper())
        codecs_text = (
            ", ".join(codecs) if codecs else self.translator.tr("file_info_unknown")
        )

        template = self.translator.tr("file_info_template")
        return template.format(
            duration=duration_text,
            resolution=resolution_text,
            codecs=codecs_text,
        )

    @staticmethod
    def _format_duration(seconds: float) -> str:
        total_seconds = int(round(seconds))
        minutes, sec = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"

    @staticmethod
    def _safe_int(value: object) -> int | None:
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None
