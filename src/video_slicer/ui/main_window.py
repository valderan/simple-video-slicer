"""Главное окно приложения."""
from __future__ import annotations

import json
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
from ..utils.settings import (
    AppSettings,
    SettingsManager,
    default_log_file,
    detect_system_language,
)
from ..utils.time_parser import format_time, parse_time
from .preview_dialog import PreviewDialog
from .segment_dialog import SegmentDialog
from .settings_dialog import SettingsDialog
from .translations import Translator

logger = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings_manager = SettingsManager()
        self.app_settings: AppSettings = self.settings_manager.load()
        if not self.app_settings.language:
            self.app_settings.language = detect_system_language()
            self.settings_manager.save(self.app_settings)

        self.translator = Translator(self.app_settings.language or "en")
        self.segment_manager = SegmentManager()
        self.input_file: Path | None = None
        self.output_dir: Path | None = None
        self._file_info: dict[str, object] | None = None
        self._stop_requested = False
        self._log_file_handler: logging.Handler | None = None

        self.setWindowTitle("SVS - Simple Video Slicer")
        self.resize(900, 600)
        self.setWindowIcon(self._create_app_icon())

        self._create_actions()
        self._create_menu()
        self._create_widgets()
        self._create_status_bar()
        self._apply_theme(self.app_settings.theme)
        self._apply_ffmpeg_path()
        self._configure_file_logging()
        self.retranslate_ui()

    def _create_app_icon(self) -> QtGui.QIcon:
        pixmap = QtGui.QPixmap(256, 256)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        gradient = QtGui.QLinearGradient(0, 0, 0, 256)
        gradient.setColorAt(0, QtGui.QColor("#3f51b5"))
        gradient.setColorAt(1, QtGui.QColor("#1a237e"))
        painter.fillRect(pixmap.rect(), gradient)

        body_rect = pixmap.rect().adjusted(40, 40, -40, -40)
        painter.setPen(QtGui.QPen(QtGui.QColor("#ffffff"), 8))
        painter.setBrush(QtGui.QColor(0, 0, 0, 90))
        painter.drawRoundedRect(body_rect, 28, 28)

        hole_brush = QtGui.QBrush(QtGui.QColor("#ffffff"))
        hole_radius = 10
        x_positions = [body_rect.left() + 28 + i * ((body_rect.width() - 56) / 4) for i in range(5)]
        for x in x_positions:
            for y in (body_rect.top() + 22, body_rect.bottom() - 22):
                painter.setBrush(hole_brush)
                painter.drawEllipse(QtCore.QPoint(int(x), int(y)), hole_radius, hole_radius)

        painter.setBrush(QtGui.QColor("#ffeb3b"))
        painter.setPen(QtGui.QPen(QtGui.QColor("#ffeb3b"), 6))
        triangle = QtGui.QPolygon(
            [
                QtCore.QPoint(body_rect.left() + body_rect.width() // 3, body_rect.top() + 40),
                QtCore.QPoint(
                    body_rect.left() + body_rect.width() // 3,
                    body_rect.bottom() - 40,
                ),
                QtCore.QPoint(
                    body_rect.right() - body_rect.width() // 4,
                    body_rect.center().y(),
                ),
            ]
        )
        painter.drawPolygon(triangle)
        painter.end()

        return QtGui.QIcon(pixmap)

    def _create_actions(self) -> None:
        self.settings_action = QtGui.QAction()
        self.settings_action.triggered.connect(self.open_settings)

        self.manual_action = QtGui.QAction()
        self.manual_action.triggered.connect(self.show_manual)

        self.about_action = QtGui.QAction()
        self.about_action.triggered.connect(self.show_about)

    def _create_menu(self) -> None:
        menubar = self.menuBar()
        self.settings_menu = menubar.addMenu("")
        self.settings_menu.addAction(self.settings_action)

        self.help_menu = menubar.addMenu("")
        self.help_menu.addAction(self.manual_action)
        self.help_menu.addAction(self.about_action)

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
        self.save_button = QtWidgets.QPushButton()
        self.save_button.clicked.connect(self.save_segments_to_file)
        self.load_button = QtWidgets.QPushButton()
        self.load_button.clicked.connect(self.load_segments_from_file)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.duplicate_button)
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
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
        self.save_button.setText(self.translator.tr("save_segments"))
        self.save_button.setToolTip(self.translator.tr("tooltip_save_segments"))
        self.load_button.setText(self.translator.tr("load_segments"))
        self.load_button.setToolTip(self.translator.tr("tooltip_load_segments"))
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
        self.settings_menu.setTitle(self.translator.tr("settings_menu"))
        self.settings_action.setText(self.translator.tr("settings_title"))
        self.help_menu.setTitle(self.translator.tr("help_menu"))
        self.manual_action.setText(self.translator.tr("help_manual"))
        self.about_action.setText(self.translator.tr("help_about"))
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
        if language not in {"ru", "en"}:
            return
        self.app_settings.language = language
        self.translator.set_language(language)
        self.settings_manager.save(self.app_settings)
        self.retranslate_ui()
        self._refresh_table()

    def open_settings(self) -> None:
        dialog = SettingsDialog(self, self.translator, self.app_settings)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        updated = dialog.get_settings()
        if not updated.language:
            updated.language = detect_system_language()

        language_changed = updated.language != self.app_settings.language
        theme_changed = updated.theme != self.app_settings.theme
        ffmpeg_changed = updated.ffmpeg_path != self.app_settings.ffmpeg_path
        logging_changed = (
            updated.log_to_file != self.app_settings.log_to_file
            or updated.log_file_path != self.app_settings.log_file_path
        )

        self.app_settings = updated

        if language_changed:
            self.set_language(updated.language or "en")

        if theme_changed:
            self._apply_theme(self.app_settings.theme)

        if ffmpeg_changed:
            self._apply_ffmpeg_path()

        if logging_changed:
            self._configure_file_logging()
        self.settings_manager.save(self.app_settings)

    def show_manual(self) -> None:
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.translator.tr("help_manual"))
        layout = QtWidgets.QVBoxLayout(dialog)
        text = QtWidgets.QTextBrowser()
        text.setPlainText(self.translator.tr("help_manual_content"))
        text.setReadOnly(True)
        text.setMinimumSize(500, 400)
        layout.addWidget(text)
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Close
        )
        close_button = button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Close)
        if close_button:
            close_button.setText(self.translator.tr("preview_close"))
        button_box.rejected.connect(dialog.reject)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        dialog.exec()

    def show_about(self) -> None:
        QtWidgets.QMessageBox.information(
            self,
            self.translator.tr("help_about"),
            self.translator.tr("about_text"),
        )

    def select_input_file(self) -> None:
        start_dir = (
            self.app_settings.last_input_dir
            or (str(self.input_file.parent) if self.input_file else None)
            or str(Path.home())
        )
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.translator.tr("file_label"),
            start_dir,
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
                self.app_settings.last_input_dir = str(self.input_file.parent)
                self.settings_manager.save(self.app_settings)
            except Exception as exc:  # noqa: BLE001
                QtWidgets.QMessageBox.critical(
                    self, self.translator.tr("error"), str(exc)
                )
                self._file_info = None
                self.file_info_label.setText(str(exc))

    def select_output_dir(self) -> None:
        start_dir = (
            self.app_settings.last_output_dir
            or (str(self.output_dir) if self.output_dir else None)
            or str(Path.home())
        )
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            self.translator.tr("output_label"),
            start_dir,
        )
        if directory:
            try:
                self.output_dir = validators.validate_output_dir(directory)
                self.output_line.setText(str(self.output_dir))
                logger.info("Выходная директория: %s", self.output_dir)
                self.app_settings.last_output_dir = str(self.output_dir)
                self.settings_manager.save(self.app_settings)
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

    def save_segments_to_file(self) -> None:
        default_dir = (
            self.app_settings.last_output_dir
            or self.app_settings.last_input_dir
            or (str(self.output_dir) if self.output_dir else None)
        )
        if default_dir:
            base_path = Path(default_dir)
            if base_path.is_dir():
                initial = base_path / "segments.json"
            else:
                initial = base_path
        else:
            initial = Path.home() / "segments.json"

        filters = ";;".join(
            [
                self.translator.tr("segments_file_filter"),
                self.translator.tr("all_files_filter"),
            ]
        )
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.translator.tr("save_segments"),
            str(initial),
            filters,
        )
        if not filename:
            return

        try:
            payload = []
            for segment in self.segment_manager.segments:
                payload.append(
                    {
                        "start_time": format_time(segment.start),
                        "end_time": ""
                        if segment.end is None
                        else format_time(segment.end),
                        "filename": segment.filename or "",
                        "format": segment.container,
                        "convert": segment.convert,
                        "video_codec": segment.video_codec,
                        "audio_codec": segment.audio_codec,
                        "crf": segment.crf,
                        "extra_params": segment.extra_args,
                    }
                )
            with open(filename, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            QtWidgets.QMessageBox.information(
                self,
                self.translator.tr("info"),
                self.translator.tr("segments_save_success"),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Не удалось сохранить список сегментов")
            QtWidgets.QMessageBox.critical(
                self,
                self.translator.tr("error"),
                f"{self.translator.tr('segments_save_error')}: {exc}",
            )

    def load_segments_from_file(self) -> None:
        default_dir = (
            self.app_settings.last_output_dir
            or self.app_settings.last_input_dir
            or (str(self.output_dir) if self.output_dir else None)
        )
        initial = default_dir or str(Path.home())
        filters = ";;".join(
            [
                self.translator.tr("segments_file_filter"),
                self.translator.tr("all_files_filter"),
            ]
        )
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.translator.tr("load_segments"),
            initial,
            filters,
        )
        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if not isinstance(data, list):
                raise ValueError("Invalid segments format")

            self.segment_manager.clear()
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                start_value = entry.get("start_time", "00:00:00")
                end_value = entry.get("end_time")
                start_time = parse_time(str(start_value))
                end_time = parse_time(str(end_value)) if end_value else None
                segment = Segment(
                    start=start_time,
                    end=end_time,
                    filename=(entry.get("filename") or None),
                    container=entry.get("format") or entry.get("container") or "mp4",
                    convert=bool(entry.get("convert", False)),
                    video_codec=entry.get("video_codec", "copy"),
                    audio_codec=entry.get("audio_codec", "copy"),
                    crf=int(entry.get("crf", 23)),
                    extra_args=entry.get("extra_params")
                    or entry.get("extra_args")
                    or "",
                )
                if not segment.convert:
                    segment.video_codec = "copy"
                    segment.audio_codec = "copy"
                    segment.extra_args = ""
                self.segment_manager.add_segment(segment)
            self._refresh_table()
            QtWidgets.QMessageBox.information(
                self,
                self.translator.tr("info"),
                self.translator.tr("segments_load_success"),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Не удалось загрузить список сегментов")
            QtWidgets.QMessageBox.critical(
                self,
                self.translator.tr("error"),
                f"{self.translator.tr('segments_load_error')}: {exc}",
            )

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

    def _apply_theme(self, theme: str) -> None:
        app = QtWidgets.QApplication.instance()
        if not app:
            return
        if theme == "dark":
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(45, 45, 48))
            palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(220, 220, 220))
            palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(30, 30, 30))
            palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(45, 45, 48))
            palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(255, 255, 255))
            palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(45, 45, 48))
            palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(230, 230, 230))
            palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(60, 63, 65))
            palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(230, 230, 230))
            palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(255, 59, 48))
            palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(98, 114, 164))
            palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(255, 255, 255))
            app.setPalette(palette)
            app.setStyleSheet(
                "QToolTip { color: #1e1e1e; background-color: #f5f5f5; border: 1px solid #333; }"
            )
        else:
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("")

    def _apply_ffmpeg_path(self) -> None:
        ffmpeg_helper.set_ffmpeg_paths(self.app_settings.ffmpeg_path)

    def _configure_file_logging(self) -> None:
        root_logger = logging.getLogger()
        if self._log_file_handler:
            root_logger.removeHandler(self._log_file_handler)
            self._log_file_handler.close()
            self._log_file_handler = None

        if not self.app_settings.log_to_file:
            return

        path_str = self.app_settings.log_file_path or str(default_log_file())
        path = Path(path_str).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(path, encoding="utf-8")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
        self._log_file_handler = handler
        self.app_settings.log_file_path = str(path)
        self.settings_manager.save(self.app_settings)
        logger.info("Включено сохранение журнала в файл: %s", path)
