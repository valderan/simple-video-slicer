"""Диалог для массового создания сегментов из текстового запроса."""
from __future__ import annotations

import re
from typing import List, Tuple

from PySide6 import QtWidgets

from ..utils.time_parser import parse_time
from .translations import Translator


class BulkSegmentDialog(QtWidgets.QDialog):
    """Запрашивает у пользователя список сегментов в текстовом виде."""

    def __init__(
        self,
        parent: QtWidgets.QWidget | None,
        translator: Translator,
    ) -> None:
        super().__init__(parent)
        self._translator = translator
        self._result: List[Tuple[float, str]] = []

        self.setWindowTitle(self._translator.tr("bulk_create_title"))
        self.setModal(True)
        self.resize(520, 380)

        description = QtWidgets.QLabel(self._translator.tr("bulk_create_description"))
        description.setWordWrap(True)

        self.text_edit = QtWidgets.QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            self._translator.tr("bulk_create_placeholder")
        )

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        ok_button = button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        if ok_button:
            ok_button.setText(self._translator.tr("ok"))
        cancel_button = button_box.button(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        if cancel_button:
            cancel_button.setText(self._translator.tr("cancel"))

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(description)
        layout.addWidget(self.text_edit)
        layout.addWidget(button_box)

    def accept(self) -> None:  # noqa: D401
        """Validate input before closing the dialog."""

        try:
            self._result = self._parse_lines(self.text_edit.toPlainText())
        except ValueError as exc:
            QtWidgets.QMessageBox.warning(
                self,
                self._translator.tr("error"),
                str(exc),
            )
            return
        super().accept()

    def get_entries(self) -> List[Tuple[float, str]]:
        return list(self._result)

    def _parse_lines(self, text: str) -> List[Tuple[float, str]]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            raise ValueError(self._translator.tr("bulk_create_error_empty"))

        entries: List[Tuple[float, str]] = []
        pattern = re.compile(r"\s*[-–—]\s*")
        for index, line in enumerate(lines, start=1):
            parts = pattern.split(line, maxsplit=1)
            if len(parts) != 2:
                raise ValueError(
                    self._translator.tr("bulk_create_error_format").format(line=index)
                )
            time_text, title = parts[0].strip(), parts[1].strip()
            if not title:
                raise ValueError(
                    self._translator.tr("bulk_create_error_title").format(line=index)
                )
            try:
                start_time = parse_time(time_text)
            except ValueError:
                raise ValueError(
                    self._translator.tr("bulk_create_error_time").format(line=index)
                ) from None
            entries.append((start_time, title))

        for idx in range(1, len(entries)):
            if entries[idx][0] <= entries[idx - 1][0]:
                raise ValueError(
                    self._translator.tr("bulk_create_error_order").format(line=idx + 1)
                )

        return entries
