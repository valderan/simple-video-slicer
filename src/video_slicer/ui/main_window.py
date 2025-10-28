"""Главное окно приложения."""
from __future__ import annotations

import json
import logging
import re
from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from ..core.segment_manager import SegmentManager
from ..models.segment import Segment
from ..utils import ffmpeg_helper, validators
from ..utils.settings import (
    AppSettings,
    SettingsManager,
    default_log_file,
    detect_system_language,
)
from ..utils.time_parser import format_time, parse_time
from .bulk_segment_dialog import BulkSegmentDialog
from .preview_dialog import PreviewDialog
from .processing_worker import ProcessingWorker
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
        self._probe_data: dict[str, object] | None = None
        self._stop_requested = False
        self._log_file_handler: logging.Handler | None = None
        self._ffmpeg_available = True
        self._interface_locked = False
        self._processing_thread: QtCore.QThread | None = None
        self._processing_worker: ProcessingWorker | None = None

        self.setWindowTitle("Simple Video Slicer")
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
        self._check_ffmpeg_availability(initial=True)

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

        self.download_ffmpeg_action = QtGui.QAction()
        self.download_ffmpeg_action.triggered.connect(self.open_ffmpeg_download)

        self.about_action = QtGui.QAction()
        self.about_action.triggered.connect(self.show_about)

    def _create_menu(self) -> None:
        menubar = self.menuBar()
        self.main_menu = menubar.addMenu("")
        self.main_menu.addAction(self.settings_action)
        self.main_menu.addAction(self.manual_action)
        self.main_menu.addAction(self.download_ffmpeg_action)
        self.main_menu.addSeparator()
        self.main_menu.addAction(self.about_action)

    def _create_widgets(self) -> None:
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)

        file_layout = QtWidgets.QHBoxLayout()
        self.file_label = QtWidgets.QLabel()
        self.file_line = QtWidgets.QLineEdit()
        self.file_line.setReadOnly(True)
        self.file_button = QtWidgets.QPushButton()
        self.file_button.clicked.connect(self.select_input_file)
        self.metadata_button = QtWidgets.QPushButton()
        self.metadata_button.clicked.connect(self.show_metadata)
        self.metadata_button.setEnabled(False)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_line)
        file_layout.addWidget(self.file_button)
        file_layout.addWidget(self.metadata_button)

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
        self.save_button = QtWidgets.QPushButton()
        self.save_button.clicked.connect(self.save_segments_to_file)
        self.load_button = QtWidgets.QPushButton()
        self.load_button.clicked.connect(self.load_segments_from_file)
        self.generate_button = QtWidgets.QPushButton()
        self.generate_button.clicked.connect(self.create_segments_from_text)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.duplicate_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.generate_button)
        button_layout.addStretch()
        self.segment_buttons = [
            self.add_button,
            self.edit_button,
            self.remove_button,
            self.duplicate_button,
            self.save_button,
            self.load_button,
            self.generate_button,
        ]

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
        table_container = QtWidgets.QWidget()
        table_container_layout = QtWidgets.QVBoxLayout(table_container)
        table_container_layout.setContentsMargins(0, 0, 0, 0)
        table_container_layout.addWidget(self.table)
        table_container_layout.addLayout(button_layout)
        table_container_layout.addLayout(progress_header_layout)
        table_container_layout.addWidget(self.progress_bar)

        log_container = QtWidgets.QWidget()
        log_layout = QtWidgets.QVBoxLayout(log_container)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.addWidget(self.log_label)
        log_layout.addWidget(self.log_console)

        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        self.main_splitter.addWidget(table_container)
        self.main_splitter.addWidget(log_container)
        self.main_splitter.setStretchFactor(0, 3)
        self.main_splitter.setStretchFactor(1, 1)

        layout.addWidget(self.main_splitter)
        layout.addLayout(process_buttons_layout)

        self.setCentralWidget(central)
        self._update_segment_controls_state()

    def _create_status_bar(self) -> None:
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

    def retranslate_ui(self) -> None:
        self.file_label.setText(self.translator.tr("file_label"))
        self.file_button.setText(self.translator.tr("browse"))
        self.metadata_button.setText(self.translator.tr("metadata_button"))
        self.output_label.setText(self.translator.tr("output_label"))
        self.output_button.setText(self.translator.tr("browse"))
        self.file_button.setToolTip(self.translator.tr("tooltip_file"))
        self.output_button.setToolTip(self.translator.tr("tooltip_output"))
        self.metadata_button.setToolTip(self.translator.tr("metadata_tooltip"))
        self.add_button.setText(self.translator.tr("add_segment"))
        self.add_button.setToolTip(self.translator.tr("tooltip_add"))
        self.edit_button.setText(self.translator.tr("edit_segment"))
        self.edit_button.setToolTip(self.translator.tr("tooltip_edit"))
        self.remove_button.setText(self.translator.tr("remove_segment"))
        self.remove_button.setToolTip(self.translator.tr("tooltip_remove"))
        self.duplicate_button.setText(self.translator.tr("duplicate_segment"))
        self.duplicate_button.setToolTip(self.translator.tr("tooltip_duplicate"))
        self.save_button.setText(self.translator.tr("save_segments"))
        self.save_button.setToolTip(self.translator.tr("tooltip_save_segments"))
        self.load_button.setText(self.translator.tr("load_segments"))
        self.load_button.setToolTip(self.translator.tr("tooltip_load_segments"))
        self.generate_button.setText(self.translator.tr("bulk_create_button"))
        self.generate_button.setToolTip(self.translator.tr("bulk_create_tooltip"))
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
        self.main_menu.setTitle(self.translator.tr("main_menu"))
        self.settings_action.setText(self.translator.tr("settings_title"))
        self.manual_action.setText(self.translator.tr("help_manual"))
        self.download_ffmpeg_action.setText(
            self.translator.tr("menu_download_ffmpeg")
        )
        self.about_action.setText(self.translator.tr("help_about"))
        self.status_bar.showMessage(self.translator.tr("status_ready"))
        if not self._ffmpeg_available:
            self.status_bar.showMessage(self.translator.tr("status_ffmpeg_missing"))
        self._update_table_headers()
        if self._file_info:
            self.file_info_label.setText(self._format_file_info(self._file_info))
        self._update_segment_controls_state()

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

    def _update_segment_controls_state(self) -> None:
        enabled = self.input_file is not None
        central = self.centralWidget()
        if central is not None and not central.isEnabled():
            enabled = False
        for button in getattr(self, "segment_buttons", []):
            button.setEnabled(enabled)
        if hasattr(self, "metadata_button"):
            self.metadata_button.setEnabled(enabled and self._probe_data is not None)

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
            self._check_ffmpeg_availability()

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

    def open_ffmpeg_download(self) -> None:
        QtGui.QDesktopServices.openUrl(
            QtCore.QUrl("https://ffmpeg.org/download.html")
        )

    def show_metadata(self) -> None:
        if not self.input_file or not self._probe_data:
            QtWidgets.QMessageBox.information(
                self,
                self.translator.tr("info"),
                self.translator.tr("metadata_not_available"),
            )
            return

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.translator.tr("metadata_dialog_title"))
        dialog.setModal(True)
        dialog.resize(640, 520)

        layout = QtWidgets.QVBoxLayout(dialog)
        header = QtWidgets.QLabel(
            self.translator.tr("metadata_file_label").format(path=str(self.input_file))
        )
        header.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(header)

        text = QtWidgets.QPlainTextEdit()
        text.setPlainText(json.dumps(self._probe_data, ensure_ascii=False, indent=2))
        text.setReadOnly(True)
        layout.addWidget(text)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Close
        )
        close_button = button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Close)
        if close_button:
            close_button.setText(self.translator.tr("preview_close"))
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.exec()

    def show_about(self) -> None:
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.translator.tr("help_about"))
        dialog.setModal(True)
        dialog.resize(420, 360)

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(16)

        logo_label = QtWidgets.QLabel()
        logo_path = Path(__file__).resolve().parent.parent / "logo.png"
        pixmap = QtGui.QPixmap(str(logo_path))
        if not pixmap.isNull():
            logo_label.setPixmap(
                pixmap.scaled(
                    96,
                    96,
                    QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation,
                )
            )
            logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(logo_label)

        title_layout = QtWidgets.QVBoxLayout()
        title_label = QtWidgets.QLabel("<b>Simple Video Slicer</b>")
        title_font = title_label.font()
        title_font.setPointSize(title_font.pointSize() + 2)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)

        version_label = QtWidgets.QLabel(
            self.translator.tr("about_version").format(version="0.1")
        )
        title_layout.addWidget(version_label)

        author_label = QtWidgets.QLabel(
            self.translator.tr("about_author").format(name="Vladimir Kundryukov")
        )
        title_layout.addWidget(author_label)

        repo_label = QtWidgets.QLabel(
            self.translator.tr("about_repo").format(
                year="2025",
                url="https://github.com/valderan/simple-video-slicer",
            )
        )
        repo_label.setOpenExternalLinks(True)
        title_layout.addWidget(repo_label)

        title_layout.addStretch()
        header_layout.addLayout(title_layout)
        layout.addLayout(header_layout)

        description = QtWidgets.QLabel(self.translator.tr("about_description"))
        description.setWordWrap(True)
        layout.addWidget(description)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        footer = QtWidgets.QLabel(self.translator.tr("about_tagline"))
        footer.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #607d8b; font-style: italic;")
        layout.addWidget(footer)

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
                self.file_line.setToolTip(file_path)
                logger.info("Выбран входной файл: %s", file_path)
                probe_data = ffmpeg_helper.probe_file(self.input_file)
                self._probe_data = probe_data
                info = self._extract_file_info(probe_data)
                self._file_info = info
                self.file_info_label.setText(self._format_file_info(info))
                self._handle_metadata_chapters(probe_data)
                self.app_settings.last_input_dir = str(self.input_file.parent)
                self.settings_manager.save(self.app_settings)
            except Exception as exc:  # noqa: BLE001
                QtWidgets.QMessageBox.critical(
                    self, self.translator.tr("error"), str(exc)
                )
                self._file_info = None
                self._probe_data = None
                self.file_info_label.setText(str(exc))
                self.file_line.clear()
                self.file_line.setToolTip("")
                self.input_file = None
            finally:
                self._update_segment_controls_state()

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
        dialog = SegmentDialog(
            self,
            self.translator,
            duration=self._get_video_duration(),
        )
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
        dialog = SegmentDialog(
            self,
            self.translator,
            segment,
            duration=self._get_video_duration(),
        )
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

    def create_segments_from_text(self) -> None:
        if not self.input_file:
            QtWidgets.QMessageBox.warning(
                self,
                self.translator.tr("error"),
                self.translator.tr("bulk_create_no_file"),
            )
            return

        dialog = BulkSegmentDialog(self, self.translator)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        entries = dialog.get_entries()
        add_numbering = dialog.should_add_numbering()
        include_description = dialog.should_include_description()
        try:
            segments_data = self._build_segments_from_entries(entries)
        except ValueError as exc:
            QtWidgets.QMessageBox.warning(
                self,
                self.translator.tr("error"),
                str(exc),
            )
            return

        if not segments_data:
            return

        if not self._confirm_segment_generation(
            segments_data,
            "bulk_create_confirm_title",
            "bulk_create_confirm_text",
        ):
            return

        self._apply_generated_segments(
            segments_data,
            "bulk_create_log",
            "bulk_create_status",
            add_numbering=add_numbering,
            include_description=include_description,
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
        self._stop_requested = False
        self.process_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(0)
        self.progress_info_label.setText(
            self.translator.tr("progress_template").format(current=0, total=total)
        )
        self.status_bar.showMessage(self.translator.tr("status_processing"))
        self.log_console.clear()
        self._start_processing_worker(segments)

    def stop_processing(self) -> None:
        if not self.stop_button.isEnabled():
            return
        self._stop_requested = True
        self.stop_button.setEnabled(False)
        if self._processing_worker:
            self._processing_worker.request_stop()
        self._append_log(self.translator.tr("processing_stop_requested"))

    def _start_processing_worker(self, segments: List[Segment]) -> None:
        if not self.input_file or not self.output_dir:
            return

        if self._processing_thread:
            self._stop_processing_thread()

        self._processing_thread = QtCore.QThread(self)
        self._processing_worker = ProcessingWorker(
            self.input_file,
            self.output_dir,
            segments,
        )
        self._processing_worker.moveToThread(self._processing_thread)
        self._processing_thread.started.connect(self._processing_worker.run)
        self._processing_worker.segment_started.connect(self._on_segment_started)
        self._processing_worker.segment_finished.connect(self._on_segment_finished)
        self._processing_worker.progress_changed.connect(self.progress_bar.setValue)
        self._processing_worker.error_occurred.connect(self._on_processing_error)
        self._processing_worker.finished.connect(self._on_processing_finished)
        self._processing_worker.stopped.connect(self._on_processing_stopped)
        self._processing_thread.finished.connect(self._cleanup_processing_thread)
        self._processing_thread.start()

    def _on_segment_started(self, index: int, total: int, name: str) -> None:
        self.progress_info_label.setText(
            self.translator.tr("progress_template").format(current=index, total=total)
        )
        self.status_bar.showMessage(
            self.translator.tr("status_processing_segment").format(
                current=index, total=total, name=name
            )
        )
        self._append_log(
            self.translator.tr("log_processing_segment").format(
                current=index, total=total, name=name
            )
        )

    def _on_segment_finished(self, index: int, total: int, name: str) -> None:
        self._append_log(
            self.translator.tr("log_segment_done").format(name=name)
        )
        if index == total:
            self.progress_bar.setValue(100)

    def _on_processing_error(self, message: str) -> None:
        logger.exception("Ошибка при обработке сегментов: %s", message)
        self._append_log(message)
        QtWidgets.QMessageBox.critical(
            self, self.translator.tr("error"), message
        )
        self._finalize_processing(success=False, stopped=False)

    def _on_processing_finished(self) -> None:
        self._append_log(self.translator.tr("processing_complete"))
        QtWidgets.QMessageBox.information(
            self,
            self.translator.tr("info"),
            self.translator.tr("processing_complete"),
        )
        self._finalize_processing(success=True, stopped=False)

    def _on_processing_stopped(self) -> None:
        self._append_log(self.translator.tr("processing_stop_ack"))
        self._finalize_processing(success=False, stopped=True)

    def _finalize_processing(self, *, success: bool, stopped: bool) -> None:
        if stopped:
            self.status_bar.showMessage(self.translator.tr("status_stopped"))
            self.progress_info_label.setText(self.translator.tr("progress_idle"))
            self.progress_bar.setValue(0)
        elif success:
            self.status_bar.showMessage(self.translator.tr("status_ready"))
            self.progress_info_label.setText(self.translator.tr("progress_idle"))
        else:
            self.status_bar.showMessage(self.translator.tr("status_ready"))
            self.progress_info_label.setText(self.translator.tr("progress_idle"))
            self.progress_bar.setValue(0)

        self.process_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self._stop_requested = False
        self._stop_processing_thread()

    def _stop_processing_thread(self) -> None:
        if self._processing_thread:
            self._processing_thread.quit()
            self._processing_thread.wait()
        self._cleanup_processing_thread()

    def _cleanup_processing_thread(self) -> None:
        if self._processing_worker:
            self._processing_worker.deleteLater()
            self._processing_worker = None
        if self._processing_thread:
            self._processing_thread.deleteLater()
            self._processing_thread = None

    def _append_log(self, message: str) -> None:
        timestamp = QtCore.QDateTime.currentDateTime().toString("HH:mm:ss")
        self.log_console.appendPlainText(f"[{timestamp}] {message}")

    def _extract_file_info(self, data: dict[str, object]) -> dict[str, object]:
        duration_raw = data.get("format", {}).get("duration")
        streams = data.get("streams", [])
        video_streams = [s for s in streams if s.get("codec_type") == "video"]
        audio_streams = [s for s in streams if s.get("codec_type") == "audio"]
        video_info = video_streams[0] if video_streams else {}
        audio_info = audio_streams[0] if audio_streams else {}
        duration_value = self._safe_float(duration_raw)
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

    def _get_video_duration(self) -> float | None:
        if not self._file_info:
            return None
        value = self._file_info.get("duration")
        if isinstance(value, (int, float)) and value > 0:
            return float(value)
        return None

    def _handle_metadata_chapters(self, data: dict[str, object]) -> None:
        raw_chapters = data.get("chapters")
        if not isinstance(raw_chapters, list):
            return

        chapters: list[tuple[float, float | None, str]] = []
        for index, entry in enumerate(raw_chapters, start=1):
            if not isinstance(entry, dict):
                continue
            start_value = self._safe_float(entry.get("start_time"))
            if start_value is None:
                continue
            end_value = self._safe_float(entry.get("end_time"))
            if end_value is not None and end_value <= start_value:
                end_value = None
            tags = entry.get("tags") if isinstance(entry.get("tags"), dict) else {}
            title = (
                tags.get("title")
                or tags.get("TITLE")
                or f"Chapter {index:02d}"
            )
            chapters.append((start_value, end_value, str(title)))

        if not chapters:
            return

        if not self._prompt_create_segments_from_chapters(chapters):
            return

        self._create_segments_from_chapters(chapters)

    def _build_segments_from_entries(
        self, entries: list[tuple[float, str | None]]
    ) -> list[tuple[float, float | None, str | None]]:
        duration = self._get_video_duration()
        segments: list[tuple[float, float | None, str | None]] = []

        for idx, (start, title) in enumerate(entries, start=1):
            if start < 0:
                raise ValueError(
                    self.translator.tr("bulk_create_error_negative").format(line=idx)
                )
            if duration is not None and start >= duration:
                raise ValueError(
                    self.translator.tr("bulk_create_error_over_duration").format(
                        line=idx
                    )
                )

            next_start = entries[idx][0] if idx < len(entries) else None
            if next_start is not None and next_start <= start:
                raise ValueError(
                    self.translator.tr("bulk_create_error_order").format(line=idx + 1)
                )
            if duration is not None and next_start is not None and next_start > duration:
                raise ValueError(
                    self.translator.tr("bulk_create_error_over_duration").format(
                        line=idx + 1
                    )
                )

            end_value: float | None
            if next_start is not None:
                end_value = next_start
            elif duration is not None:
                if duration <= start:
                    raise ValueError(
                        self.translator.tr("bulk_create_error_last_segment")
                    )
                end_value = duration
            else:
                end_value = None

            segments.append((start, end_value, title))

        return segments

    def _confirm_segment_generation(
        self,
        entries: list[tuple[float, float | None, str]],
        title_key: str,
        text_key: str,
    ) -> bool:
        message = QtWidgets.QMessageBox(self)
        message.setIcon(QtWidgets.QMessageBox.Icon.Question)
        message.setWindowTitle(self.translator.tr(title_key))
        message.setText(
            self.translator.tr(text_key).format(count=len(entries))
        )
        if self.segment_manager.segments:
            message.setInformativeText(
                self.translator.tr("chapters_replace_question")
            )

        details = []
        for idx, (start, end, title) in enumerate(entries, start=1):
            start_text = format_time(start)
            end_text = (
                format_time(end)
                if end is not None
                else self.translator.tr("chapters_until_end")
            )
            details.append(f"{idx:02d}. {start_text} - {end_text} — {title}")
        if details:
            message.setDetailedText("\n".join(details))

        message.setStandardButtons(
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No
        )
        yes_button = message.button(QtWidgets.QMessageBox.StandardButton.Yes)
        if yes_button:
            yes_button.setText(self.translator.tr("yes"))
        no_button = message.button(QtWidgets.QMessageBox.StandardButton.No)
        if no_button:
            no_button.setText(self.translator.tr("no"))
        return message.exec() == QtWidgets.QMessageBox.StandardButton.Yes

    def _apply_generated_segments(
        self,
        entries: list[tuple[float, float | None, str | None]],
        log_key: str,
        status_key: str,
        *,
        add_numbering: bool = False,
        include_description: bool = True,
    ) -> None:
        self.segment_manager.clear()
        default_container = (
            self.input_file.suffix.lstrip(".")
            if self.input_file and self.input_file.suffix
            else "mp4"
        )
        for idx, (start, end, title) in enumerate(entries, start=1):
            description = (title or "").strip()
            fallback_name = self._generate_default_segment_name(start)
            parts: list[str] = []
            if add_numbering:
                parts.append(str(idx))
            if include_description:
                if not description:
                    description = fallback_name
                parts.append(description)
            if not parts:
                parts.append(fallback_name)

            filename_source = "_".join(parts)
            filename = self._sanitize_filename(filename_source)
            if not filename:
                filename = fallback_name
            segment = Segment(
                start=start,
                end=end,
                filename=filename or None,
                container=default_container,
            )
            self.segment_manager.add_segment(segment)
        self._refresh_table()
        self._append_log(
            self.translator.tr(log_key).format(count=len(entries))
        )
        if hasattr(self, "status_bar"):
            self.status_bar.showMessage(
                self.translator.tr(status_key).format(count=len(entries))
            )

    def _prompt_create_segments_from_chapters(
        self, chapters: list[tuple[float, float | None, str]]
    ) -> bool:
        return self._confirm_segment_generation(
            chapters,
            "chapters_detected_title",
            "chapters_detected_text",
        )

    def _create_segments_from_chapters(
        self, chapters: list[tuple[float, float | None, str]]
    ) -> None:
        self._apply_generated_segments(
            chapters,
            "chapters_created",
            "chapters_created_status",
        )

    @staticmethod
    def _generate_default_segment_name(start: float) -> str:
        safe_start = max(0.0, start)
        total_millis = int(round(safe_start * 1000))
        millis = total_millis % 1000
        total_seconds = total_millis // 1000
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60
        hours = total_minutes // 60

        parts: list[str] = []
        if hours > 0:
            parts.append(str(hours))
            parts.append(f"{minutes:02d}")
        else:
            parts.append(str(minutes))
        parts.append(f"{seconds:02d}")
        if millis:
            parts.append(f"{millis:03d}")
        return "segment_" + "_".join(parts)

    @staticmethod
    def _sanitize_filename(value: str) -> str:
        cleaned = re.sub(r"[\\/:*?\"<>|]", "_", value)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned = cleaned.replace(" ", "_")
        cleaned = re.sub(r"_+", "_", cleaned)
        cleaned = cleaned.strip("_.")
        return cleaned[:80]

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

    @staticmethod
    def _safe_float(value: object) -> float | None:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
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

    def _set_interface_enabled(self, enabled: bool) -> None:
        central = self.centralWidget()
        if not central:
            return
        if central.isEnabled() == enabled and self._interface_locked == (not enabled):
            return
        central.setEnabled(enabled)
        self._interface_locked = not enabled
        if enabled:
            self._update_segment_controls_state()

    def _check_ffmpeg_availability(self, *, initial: bool = False) -> None:
        try:
            ffmpeg_helper.ensure_ffmpeg_available()
        except FileNotFoundError as exc:
            if self._ffmpeg_available:
                logger.warning("FFmpeg не найден: %s", exc)
                if hasattr(self, "log_console"):
                    self._append_log(self.translator.tr("log_ffmpeg_missing"))
            self._ffmpeg_available = False
            self._set_interface_enabled(False)
            if hasattr(self, "status_bar"):
                self.status_bar.showMessage(self.translator.tr("status_ffmpeg_missing"))
            return

        if not self._ffmpeg_available:
            logger.info("FFmpeg найден и готов к работе")
            if hasattr(self, "log_console"):
                self._append_log(self.translator.tr("log_ffmpeg_ready"))
        self._ffmpeg_available = True
        self._set_interface_enabled(True)
        if hasattr(self, "status_bar") and not initial:
            self.status_bar.showMessage(self.translator.tr("status_ready"))

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
