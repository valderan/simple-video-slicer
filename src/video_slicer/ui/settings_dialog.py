"""Диалог настроек приложения."""
from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from ..utils import ffmpeg_helper, path_utils
from ..utils.settings import AppSettings, default_log_file
from .translations import Translator


class SettingsDialog(QtWidgets.QDialog):
    """Диалоговое окно редактирования настроек приложения."""

    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        translator: Translator,
        settings: AppSettings,
    ) -> None:
        super().__init__(parent)
        self.translator = translator
        self._settings = settings.clone()

        self.setModal(True)
        self.setWindowTitle(self.translator.tr("settings_title"))

        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItem(self.translator.tr("language_ru"), "ru")
        self.language_combo.addItem(self.translator.tr("language_en"), "en")

        if self._settings.language and self._settings.language in {"ru", "en"}:
            index = self.language_combo.findData(self._settings.language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)

        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItem(self.translator.tr("theme_light"), "light")
        self.theme_combo.addItem(self.translator.tr("theme_dark"), "dark")
        index = self.theme_combo.findData(self._settings.theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        self.ffmpeg_edit = QtWidgets.QLineEdit(
            self._native_path(self._settings.ffmpeg_path)
            if self._settings.ffmpeg_path
            else ""
        )
        self.ffmpeg_edit.setPlaceholderText(
            self.translator.tr("settings_ffmpeg_placeholder")
        )
        self.ffmpeg_browse = QtWidgets.QToolButton()
        self.ffmpeg_browse.setText("…")
        self.ffmpeg_browse.clicked.connect(self._choose_ffmpeg)

        self.ffmpeg_auto_button = QtWidgets.QPushButton(
            self.translator.tr("settings_detect_ffmpeg")
        )
        self.ffmpeg_auto_button.clicked.connect(self._detect_ffmpeg)

        self.log_checkbox = QtWidgets.QCheckBox(
            self.translator.tr("settings_enable_logging")
        )
        self.log_checkbox.setChecked(self._settings.log_to_file)
        self.log_checkbox.toggled.connect(self._toggle_log_widgets)

        self.log_path_edit = QtWidgets.QLineEdit(
            self._native_path(self._settings.log_file_path)
            if self._settings.log_file_path
            else ""
        )
        self.log_path_edit.setPlaceholderText(
            self._native_path(str(default_log_file()))
        )
        self.log_browse = QtWidgets.QToolButton()
        self.log_browse.setText("…")
        self.log_browse.clicked.connect(self._choose_log_file)

        self.strip_metadata_checkbox = QtWidgets.QCheckBox(
            self.translator.tr("settings_strip_metadata")
        )
        self.strip_metadata_checkbox.setChecked(self._settings.strip_metadata)

        self.embed_metadata_checkbox = QtWidgets.QCheckBox(
            self.translator.tr("settings_embed_metadata")
        )
        self.embed_metadata_checkbox.setChecked(self._settings.embed_svs_metadata)

        self.icon_buttons_checkbox = QtWidgets.QCheckBox(
            self.translator.tr("settings_use_icons")
        )
        self.icon_buttons_checkbox.setChecked(self._settings.use_icon_buttons)

        ffmpeg_layout = QtWidgets.QHBoxLayout()
        ffmpeg_layout.addWidget(self.ffmpeg_edit)
        ffmpeg_layout.addWidget(self.ffmpeg_browse)

        log_layout = QtWidgets.QHBoxLayout()
        log_layout.addWidget(self.log_path_edit)
        log_layout.addWidget(self.log_browse)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.translator.tr("settings_language"), self.language_combo)
        form_layout.addRow(self.translator.tr("settings_theme"), self.theme_combo)
        form_layout.addRow(self.translator.tr("settings_ffmpeg"), ffmpeg_layout)
        form_layout.addRow("", self.ffmpeg_auto_button)
        form_layout.addRow(self.log_checkbox)
        form_layout.addRow(self.translator.tr("settings_log_file"), log_layout)
        form_layout.addRow(self.strip_metadata_checkbox)
        form_layout.addRow(self.embed_metadata_checkbox)
        form_layout.addRow(self.icon_buttons_checkbox)

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        self._toggle_log_widgets(self.log_checkbox.isChecked())

    def _choose_ffmpeg(self) -> None:
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            self.translator.tr("settings_ffmpeg"),
            self.ffmpeg_edit.text() or str(Path.home()),
        )
        if filename:
            self.ffmpeg_edit.setText(self._native_path(filename))

    def _detect_ffmpeg(self) -> None:
        try_paths = [ffmpeg_helper.current_ffmpeg(), "ffmpeg"]
        for candidate in try_paths:
            path = Path(candidate)
            if path.exists():
                self.ffmpeg_edit.setText(self._native_path(str(path)))
                return
        found = QtCore.QStandardPaths.findExecutable("ffmpeg")
        if found:
            self.ffmpeg_edit.setText(self._native_path(found))

    def _choose_log_file(self) -> None:
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            self.translator.tr("settings_log_file"),
            self.log_path_edit.text() or str(default_log_file()),
            "Log files (*.log *.txt);;All files (*)",
        )
        if filename:
            self.log_path_edit.setText(self._native_path(filename))

    def _toggle_log_widgets(self, enabled: bool) -> None:
        self.log_path_edit.setEnabled(enabled)
        self.log_browse.setEnabled(enabled)
        if enabled and not self.log_path_edit.text():
            self.log_path_edit.setText(self._native_path(str(default_log_file())))

    def get_settings(self) -> AppSettings:
        result = self._settings.clone()
        result.language = self.language_combo.currentData()
        result.theme = self.theme_combo.currentData()
        ffmpeg_path = self.ffmpeg_edit.text().strip()
        result.ffmpeg_path = self._normalize_path_value(ffmpeg_path)
        result.log_to_file = self.log_checkbox.isChecked()
        log_path = self.log_path_edit.text().strip()
        result.log_file_path = self._normalize_path_value(log_path)
        result.strip_metadata = self.strip_metadata_checkbox.isChecked()
        result.embed_svs_metadata = self.embed_metadata_checkbox.isChecked()
        result.use_icon_buttons = self.icon_buttons_checkbox.isChecked()
        return result

    @staticmethod
    def _native_path(path: str) -> str:
        return QtCore.QDir.toNativeSeparators(path)

    @staticmethod
    def _normalize_path_value(value: str) -> str | None:
        normalized = path_utils.normalize_user_path(value)
        if not normalized:
            return None
        return str(Path(normalized).expanduser())
