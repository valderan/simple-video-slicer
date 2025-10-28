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
        self._result: List[Tuple[float, str | None]] = []

        self.setWindowTitle(self._translator.tr("bulk_create_title"))
        self.setModal(True)
        self.resize(520, 380)

        description = QtWidgets.QLabel(self._translator.tr("bulk_create_description"))
        description.setWordWrap(True)

        self.text_edit = QtWidgets.QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            self._translator.tr("bulk_create_placeholder")
        )

        self.numbering_checkbox = QtWidgets.QCheckBox(
            self._translator.tr("bulk_create_option_numbering")
        )
        self.numbering_checkbox.setChecked(True)
        self.description_checkbox = QtWidgets.QCheckBox(
            self._translator.tr("bulk_create_option_description")
        )
        self.description_checkbox.setChecked(True)

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

        options_layout = QtWidgets.QHBoxLayout()
        options_layout.addWidget(self.numbering_checkbox)
        options_layout.addWidget(self.description_checkbox)
        options_layout.addStretch()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(description)
        layout.addLayout(options_layout)
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

    def get_entries(self) -> List[Tuple[float, str | None]]:
        return list(self._result)

    def should_add_numbering(self) -> bool:
        return self.numbering_checkbox.isChecked()

    def should_include_description(self) -> bool:
        return self.description_checkbox.isChecked()

    def _parse_lines(self, text: str) -> List[Tuple[float, str | None]]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            raise ValueError(self._translator.tr("bulk_create_error_empty"))

        time_pattern = re.compile(
            r"^(?P<time>(?:\d{1,2}:){1,2}\d{1,2}(?:\.\d{1,3})?|\d+(?:\.\d{1,3})?)\s*(?P<rest>.*)$"
        )
        entries: List[Tuple[float, str | None]] = []
        for index, line in enumerate(lines, start=1):
            match = time_pattern.match(line)
            if not match:
                raise ValueError(
                    self._translator.tr("bulk_create_error_format").format(line=index)
                )
            time_text = match.group("time").strip()
            remainder = match.group("rest") or ""
            raw_tail = remainder
            remainder = remainder.strip()

            has_dash = False
            if remainder.startswith(("-", "–", "—")):
                has_dash = True
                remainder = remainder[1:].strip()

            if has_dash and not remainder:
                raise ValueError(
                    self._translator.tr("bulk_create_error_title").format(line=index)
                )

            try:
                start_time = parse_time(time_text)
            except ValueError:
                raise ValueError(
                    self._translator.tr("bulk_create_error_time").format(line=index)
                ) from None

            title = remainder if remainder else (raw_tail.strip() or None)
            entries.append((start_time, title))

        for idx in range(1, len(entries)):
            if entries[idx][0] <= entries[idx - 1][0]:
                raise ValueError(
                    self._translator.tr("bulk_create_error_order").format(line=idx + 1)
                )

        return entries
