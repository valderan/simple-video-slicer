"""Диалог добавления/редактирования сегмента."""
from __future__ import annotations

from dataclasses import replace

from PySide6 import QtWidgets

from ..models.segment import Segment
from ..utils.time_parser import format_time, parse_time
from .translations import Translator


class SegmentDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        translator: Translator,
        segment: Segment | None = None,
    ) -> None:
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.tr("dialog_title"))
        self.setModal(True)

        self.segment = replace(segment) if segment else Segment(start=0.0)

        self.filename_edit = QtWidgets.QLineEdit(self.segment.filename or "")
        start_value = (
            format_time(self.segment.start)
            if self.segment.start
            else "00:00:00.000"
        )
        self.start_edit = QtWidgets.QLineEdit(start_value)
        self.end_edit = QtWidgets.QLineEdit(
            "" if self.segment.end is None else format_time(self.segment.end)
        )
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(["mp4", "mkv", "avi", "webm", "mov", "flv"])
        if self.segment.container:
            index = self.format_combo.findText(self.segment.container)
            if index >= 0:
                self.format_combo.setCurrentIndex(index)
        self.convert_checkbox = QtWidgets.QCheckBox()
        self.convert_checkbox.setChecked(self.segment.convert)
        self.convert_checkbox.toggled.connect(self._update_conversion_state)

        self.conversion_group = QtWidgets.QGroupBox()
        conversion_layout = QtWidgets.QFormLayout()
        self.video_codec_combo = QtWidgets.QComboBox()
        self.video_codec_combo.addItems(["copy", "h264", "hevc", "vp9", "av1"])
        self.audio_codec_combo = QtWidgets.QComboBox()
        self.audio_codec_combo.addItems(["copy", "aac", "mp3", "opus", "vorbis"])
        self.crf_spin = QtWidgets.QSpinBox()
        self.crf_spin.setRange(0, 51)
        self.crf_spin.setValue(self.segment.crf)
        self.extra_args_edit = QtWidgets.QLineEdit(self.segment.extra_args)

        for combo, value in [
            (self.video_codec_combo, self.segment.video_codec),
            (self.audio_codec_combo, self.segment.audio_codec),
        ]:
            index = combo.findText(value)
            if index >= 0:
                combo.setCurrentIndex(index)

        conversion_layout.addRow(self.translator.tr("video_codec"), self.video_codec_combo)
        conversion_layout.addRow(self.translator.tr("audio_codec"), self.audio_codec_combo)
        conversion_layout.addRow(self.translator.tr("crf"), self.crf_spin)
        conversion_layout.addRow(self.translator.tr("extra"), self.extra_args_edit)
        self.conversion_group.setLayout(conversion_layout)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.translator.tr("filename"), self.filename_edit)
        form_layout.addRow(self.translator.tr("start_time"), self.start_edit)
        form_layout.addRow(self.translator.tr("end_time"), self.end_edit)
        form_layout.addRow(self.translator.tr("format"), self.format_combo)
        form_layout.addRow(self.translator.tr("convert"), self.convert_checkbox)

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.conversion_group)
        layout.addWidget(self.button_box)

        self._retranslate_ui()
        self._update_conversion_state(self.convert_checkbox.isChecked())

    def _retranslate_ui(self) -> None:
        self.setWindowTitle(self.translator.tr("dialog_title"))
        self.filename_edit.setPlaceholderText(
            self.translator.tr("filename_placeholder")
        )
        self.start_edit.setPlaceholderText(self.translator.tr("start_placeholder"))
        self.end_edit.setPlaceholderText(self.translator.tr("end_placeholder"))
        self.conversion_group.setTitle(self.translator.tr("conversion_settings"))
        self.convert_checkbox.setText(self.translator.tr("convert_checkbox"))
        self.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Ok).setText(
            self.translator.tr("ok")
        )
        self.button_box.button(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        ).setText(self.translator.tr("cancel"))

    def _update_conversion_state(self, enabled: bool) -> None:
        self.conversion_group.setEnabled(enabled)

    def get_segment(self) -> Segment:
        start_time = parse_time(self.start_edit.text())
        end_text = self.end_edit.text().strip()
        end_time = parse_time(end_text) if end_text else None
        filename = self.filename_edit.text().strip() or None
        container = self.format_combo.currentText()
        convert = self.convert_checkbox.isChecked()

        segment = replace(self.segment)
        segment.start = start_time
        segment.end = end_time
        segment.filename = filename
        segment.container = container
        segment.convert = convert
        segment.crf = self.crf_spin.value()
        if convert:
            segment.video_codec = self.video_codec_combo.currentText()
            segment.audio_codec = self.audio_codec_combo.currentText()
            segment.extra_args = self.extra_args_edit.text().strip()
        else:
            segment.video_codec = "copy"
            segment.audio_codec = "copy"
            segment.extra_args = ""
        return segment
