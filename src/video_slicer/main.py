"""Точка входа приложения Simple Video Slicer."""
from __future__ import annotations

import logging
import sys

from PySide6 import QtWidgets

from .ui.main_window import MainWindow


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logging.info("Приложение Simple Video Slicer запущено")


def main() -> int:
    configure_logging()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    result = app.exec()
    logging.info("Приложение Simple Video Slicer завершено")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
