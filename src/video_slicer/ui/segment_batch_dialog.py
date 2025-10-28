"""Диалог для массового изменения параметров сегментов."""
from __future__ import annotations

from dataclasses import replace
from typing import Iterable, List

from PySide6 import QtWidgets

from ..models.segment import Segment
from .translations import Translator


class SegmentBatchDialog(QtWidgets.QDialog):
    """Позволяет применить параметры формата и конвертации к группе сегментов."""

    _CONTAINERS = ["mp4", "mkv", "avi", "webm", "mov", "flv"]
    _VIDEO_CODECS = ["copy", "h264", "hevc", "vp9", "av1"]
    _AUDIO_CODECS = ["copy", "aac", "mp3", "opus", "vorbis"]

    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        translator: Translator,
        segments: Iterable[Segment],
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._segments: List[Segment] = [replace(segment) for segment in segments]
        reference = self._segments[0] if self._segments else Segment(start=0.0)

        self.setWindowTitle(self._translator.tr("batch_edit_title"))
        self.setModal(True)

        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(self._CONTAINERS)
        if reference.container:
            index = self.format_combo.findText(reference.container)
            if index >= 0:
                self.format_combo.setCurrentIndex(index)

        self.convert_checkbox = QtWidgets.QCheckBox()
        self.convert_checkbox.setChecked(reference.convert)
        self.convert_checkbox.toggled.connect(self._toggle_conversion_group)

        self.conversion_group = QtWidgets.QGroupBox()
        conversion_layout = QtWidgets.QFormLayout()
        self.video_codec_combo = QtWidgets.QComboBox()
        self.video_codec_combo.addItems(self._VIDEO_CODECS)
        self.audio_codec_combo = QtWidgets.QComboBox()
        self.audio_codec_combo.addItems(self._AUDIO_CODECS)
        self.crf_spin = QtWidgets.QSpinBox()
        self.crf_spin.setRange(0, 51)
        self.crf_spin.setValue(reference.crf)
        self.extra_args_edit = QtWidgets.QLineEdit(reference.extra_args)
        self.extra_args_edit.setClearButtonEnabled(True)

        for combo, value in [
            (self.video_codec_combo, reference.video_codec),
            (self.audio_codec_combo, reference.audio_codec),
        ]:
            index = combo.findText(value)
            if index >= 0:
                combo.setCurrentIndex(index)

        conversion_layout.addRow(
            self._translator.tr("video_codec"),
            self.video_codec_combo,
        )
        conversion_layout.addRow(
            self._translator.tr("audio_codec"),
            self.audio_codec_combo,
        )
        conversion_layout.addRow(
            self._translator.tr("crf"),
            self.crf_spin,
        )
        conversion_layout.addRow(
            self._translator.tr("extra"),
            self.extra_args_edit,
        )
        self.conversion_group.setLayout(conversion_layout)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self._translator.tr("format"), self.format_combo)
        form_layout.addRow(self._translator.tr("convert"), self.convert_checkbox)

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        ok_button = self.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        if ok_button:
            ok_button.setText(self._translator.tr("ok"))
        cancel_button = self.button_box.button(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        if cancel_button:
            cancel_button.setText(self._translator.tr("cancel"))

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.conversion_group)
        layout.addWidget(self.button_box)

        self._retranslate_dynamic()
        self._toggle_conversion_group(self.convert_checkbox.isChecked())

    def _toggle_conversion_group(self, enabled: bool) -> None:
        self.conversion_group.setEnabled(enabled)

    def _retranslate_dynamic(self) -> None:
        hint = self._translator.tr("extra_hint")
        self.extra_args_edit.setPlaceholderText(hint)
        self.extra_args_edit.setToolTip(hint)
        self.convert_checkbox.setText(self._translator.tr("convert_checkbox"))
        self.conversion_group.setTitle(self._translator.tr("conversion_settings"))

    def get_result(self) -> tuple[str, bool, str, str, int, str]:
        container = self.format_combo.currentText()
        convert = self.convert_checkbox.isChecked()
        video_codec = self.video_codec_combo.currentText()
        audio_codec = self.audio_codec_combo.currentText()
        crf = self.crf_spin.value()
        extra_args = self.extra_args_edit.text().strip()
        if not convert:
            video_codec = "copy"
            audio_codec = "copy"
            extra_args = ""
        return container, convert, video_codec, audio_codec, crf, extra_args
