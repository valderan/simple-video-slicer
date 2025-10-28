"""Главное окно приложения."""
from __future__ import annotations

import logging
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

        output_layout = QtWidgets.QHBoxLayout()
        self.output_label = QtWidgets.QLabel()
        self.output_line = QtWidgets.QLineEdit()
        self.output_line.setReadOnly(True)
        self.output_button = QtWidgets.QPushButton()
        self.output_button.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(self.output_button)

        self.table = QtWidgets.QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "#",
            self.translator.tr("filename"),
            self.translator.tr("start_time"),
            self.translator.tr("end_time"),
            self.translator.tr("preview"),
        ])
        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(
            QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked
            | QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked
        )

        button_layout = QtWidgets.QHBoxLayout()
        self.add_button = QtWidgets.QPushButton()
        self.add_button.clicked.connect(self.add_segment)
        self.remove_button = QtWidgets.QPushButton()
        self.remove_button.clicked.connect(self.remove_segment)
        self.preview_button = QtWidgets.QPushButton()
        self.preview_button.clicked.connect(self.preview_segment)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.preview_button)
        button_layout.addStretch()

        options_layout = QtWidgets.QGridLayout()
        self.video_codec_label = QtWidgets.QLabel()
        self.video_codec_combo = QtWidgets.QComboBox()
        self.video_codec_combo.addItems(["copy", "h264", "hevc", "vp9", "av1"])
        self.audio_codec_label = QtWidgets.QLabel()
        self.audio_codec_combo = QtWidgets.QComboBox()
        self.audio_codec_combo.addItems(["copy", "aac", "mp3", "opus", "vorbis"])
        self.crf_label = QtWidgets.QLabel()
        self.crf_spin = QtWidgets.QSpinBox()
        self.crf_spin.setRange(0, 51)
        self.crf_spin.setValue(23)
        self.extra_label = QtWidgets.QLabel()
        self.extra_line = QtWidgets.QLineEdit()

        options_layout.addWidget(self.video_codec_label, 0, 0)
        options_layout.addWidget(self.video_codec_combo, 0, 1)
        options_layout.addWidget(self.audio_codec_label, 1, 0)
        options_layout.addWidget(self.audio_codec_combo, 1, 1)
        options_layout.addWidget(self.crf_label, 2, 0)
        options_layout.addWidget(self.crf_spin, 2, 1)
        options_layout.addWidget(self.extra_label, 3, 0)
        options_layout.addWidget(self.extra_line, 3, 1)

        self.process_button = QtWidgets.QPushButton()
        self.process_button.clicked.connect(self.process_segments)

        layout.addLayout(file_layout)
        layout.addWidget(self.file_info_label)
        layout.addLayout(output_layout)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        layout.addLayout(options_layout)
        layout.addWidget(self.process_button)

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
        self.remove_button.setText(self.translator.tr("remove_segment"))
        self.remove_button.setToolTip(self.translator.tr("tooltip_remove"))
        self.preview_button.setText(self.translator.tr("preview"))
        self.preview_button.setToolTip(self.translator.tr("tooltip_preview"))
        self.video_codec_label.setText(self.translator.tr("video_codec"))
        self.audio_codec_label.setText(self.translator.tr("audio_codec"))
        self.crf_label.setText(self.translator.tr("crf"))
        self.extra_label.setText(self.translator.tr("extra"))
        self.process_button.setText(self.translator.tr("process"))
        self.process_button.setToolTip(self.translator.tr("tooltip_process"))
        self.file_line.setToolTip(self.file_line.text())
        self.output_line.setToolTip(self.output_line.text())
        self.table.setToolTip(self.translator.tr("segment_table"))
        self.video_codec_combo.setToolTip(self.translator.tr("video_codec"))
        self.audio_codec_combo.setToolTip(self.translator.tr("audio_codec"))
        self.crf_spin.setToolTip(self.translator.tr("crf"))
        self.extra_line.setToolTip(self.translator.tr("extra"))
        self.help_menu.setTitle(self.translator.tr("help_menu"))
        self.help_action.setText(self.translator.tr("help_manual"))
        self.language_menu.setTitle(self.translator.tr("language_menu"))
        self.lang_ru_action.setText(self.translator.tr("language_ru"))
        self.lang_en_action.setText(self.translator.tr("language_en"))
        self.status_bar.showMessage(self.translator.tr("status_ready"))
        self._update_table_headers()

    def _update_table_headers(self) -> None:
        headers = [
            "#",
            self.translator.tr("filename"),
            self.translator.tr("start_time"),
            self.translator.tr("end_time"),
            self.translator.tr("preview"),
        ]
        for idx, text in enumerate(headers):
            item = self.table.horizontalHeaderItem(idx)
            if item:
                item.setText(text)

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
                self.file_info_label.setText(info)
            except Exception as exc:  # noqa: BLE001
                QtWidgets.QMessageBox.critical(
                    self, self.translator.tr("error"), str(exc)
                )

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
                start, end, filename = dialog.get_values()
                segment = Segment(
                    start=start,
                    end=end,
                    filename=filename,
                    video_codec=self.video_codec_combo.currentText(),
                    audio_codec=self.audio_codec_combo.currentText(),
                    crf=self.crf_spin.value(),
                    extra_args=self.extra_line.text().strip(),
                )
                self.segment_manager.add_segment(segment)
                logger.info("Добавлен сегмент #%s (%s-%s)", segment.index, start, end)
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

    def preview_segment(self) -> None:
        if not self.input_file:
            return
        row = self.table.currentRow()
        if row < 0:
            return
        segment = self.segment_manager.get(row)
        if not segment:
            return
        dialog = PreviewDialog(self, self.translator, self.input_file, segment.start)
        dialog.exec()

    def _refresh_table(self) -> None:
        self.table.setRowCount(len(self.segment_manager.segments))
        for row, segment in enumerate(self.segment_manager.segments):
            values = [
                str(segment.index),
                segment.filename or "",
                format_time(segment.start),
                "" if segment.end is None else format_time(segment.end),
                "▶",
            ]
            for col, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                if col == 0:
                    item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, col, item)

    def _collect_segments_from_table(self) -> List[Segment]:
        segments: List[Segment] = []
        for row in range(self.table.rowCount()):
            start_item = self.table.item(row, 2)
            end_item = self.table.item(row, 3)
            filename_item = self.table.item(row, 1)
            start = validators.parse_table_time(start_item.text() if start_item else "")
            end = (
                validators.parse_table_time(end_item.text()) if end_item and end_item.text() else None
            )
            segment = self.segment_manager.get(row)
            if segment is None:
                segment = Segment(start=start, end=end)
            else:
                segment.start = start
                segment.end = end
            segment.filename = filename_item.text().strip() if filename_item else None
            segment.video_codec = self.video_codec_combo.currentText()
            segment.audio_codec = self.audio_codec_combo.currentText()
            segment.crf = self.crf_spin.value()
            segment.extra_args = self.extra_line.text().strip()
            segments.append(segment)
        return segments

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
        try:
            validators.ensure_ffmpeg_available()
            segments = self._collect_segments_from_table()
            processor = VideoProcessor(self.input_file, self.output_dir)
            processor.slice_segments(segments)
            logger.info("Обработка завершена для %s сегментов", len(segments))
            QtWidgets.QMessageBox.information(
                self,
                self.translator.tr("info"),
                "Обработка завершена успешно",
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Ошибка при обработке сегментов")
            QtWidgets.QMessageBox.critical(
                self, self.translator.tr("error"), str(exc)
            )

    def _probe_file(self, path: Path) -> str:
        try:
            data = ffmpeg_helper.probe_file(path)
            duration = data.get("format", {}).get("duration")
            streams = data.get("streams", [])
            video_streams = [s for s in streams if s.get("codec_type") == "video"]
            audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
            video_info = video_streams[0] if video_streams else {}
            audio_info = audio_streams[0] if audio_streams else {}
            duration_text = (
                f"Длительность: {float(duration):.2f} c" if duration else ""
            )
            video_text = (
                f"Видео: {video_info.get('codec_name', '')} {video_info.get('width', '')}x{video_info.get('height', '')}"
            )
            audio_text = f"Аудио: {audio_info.get('codec_name', '')}"
            return ", ".join(filter(None, [duration_text, video_text, audio_text]))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Не удалось получить информацию о файле")
            return str(exc)
