"""Диалог добавления/редактирования сегмента."""
from __future__ import annotations

from PySide6 import QtWidgets

from ..utils.time_parser import parse_time, format_time
from .translations import Translator


class SegmentDialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        translator: Translator,
        start: float | None = None,
        end: float | None = None,
        filename: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.tr("dialog_title"))
        self.setModal(True)

        self.start_edit = QtWidgets.QLineEdit(
            format_time(start) if start is not None else "00:00:00.000"
        )
        self.end_edit = QtWidgets.QLineEdit(
            "" if end is None else format_time(end)
        )
        self.filename_edit = QtWidgets.QLineEdit(filename or "")

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.translator.tr("start_time"), self.start_edit)
        form_layout.addRow(self.translator.tr("end_time"), self.end_edit)
        form_layout.addRow(self.translator.tr("filename"), self.filename_edit)

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.button_box)

    def get_values(self) -> tuple[float, float | None, str | None]:
        start_time = parse_time(self.start_edit.text())
        end_text = self.end_edit.text().strip()
        end_time = parse_time(end_text) if end_text else None
        filename = self.filename_edit.text().strip() or None
        return start_time, end_time, filename
