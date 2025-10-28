"""Utilities for working with persistent application settings."""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from PySide6 import QtCore


def detect_system_language() -> str:
    """Return the preferred language based on the system locale."""

    locale = QtCore.QLocale.system()
    if locale.language() == QtCore.QLocale.Language.Russian:
        return "ru"
    return "en"


def default_log_file() -> Path:
    """Return the default log file location."""

    base_dir = Path(QtCore.QStandardPaths.writableLocation(
        QtCore.QStandardPaths.StandardLocation.AppDataLocation
    ))
    if not base_dir:
        base_dir = Path.home() / ".simple-video-slicer"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / "svs.log"


@dataclass
class AppSettings:
    """Container for the application settings."""

    language: str | None = None
    theme: str = "light"
    ffmpeg_path: str | None = None
    log_to_file: bool = False
    log_file_path: str | None = None
    last_input_dir: str | None = None
    last_output_dir: str | None = None

    def clone(self) -> "AppSettings":
        return replace(self)


class SettingsManager:
    """Helper class that reads/writes settings via QSettings."""

    ORGANIZATION = "SimpleVideoSlicer"
    APPLICATION = "SVS"

    def __init__(self) -> None:
        self._settings = QtCore.QSettings(self.ORGANIZATION, self.APPLICATION)

    def load(self) -> AppSettings:
        data = AppSettings(
            language=self._settings.value("language", type=str),
            theme=self._settings.value("theme", "light", str),
            ffmpeg_path=self._settings.value("ffmpeg_path", type=str),
            log_to_file=self._settings.value("log_to_file", False, bool),
            log_file_path=self._settings.value("log_file_path", type=str),
            last_input_dir=self._settings.value("last_input_dir", type=str),
            last_output_dir=self._settings.value("last_output_dir", type=str),
        )
        if data.language not in {"ru", "en"}:
            data.language = None
        if data.theme not in {"light", "dark"}:
            data.theme = "light"
        return data

    def save(self, settings: AppSettings) -> None:
        self._settings.setValue("language", settings.language)
        self._settings.setValue("theme", settings.theme)
        self._settings.setValue("ffmpeg_path", settings.ffmpeg_path)
        self._settings.setValue("log_to_file", settings.log_to_file)
        self._settings.setValue("log_file_path", settings.log_file_path)
        self._settings.setValue("last_input_dir", settings.last_input_dir)
        self._settings.setValue("last_output_dir", settings.last_output_dir)
        self._settings.sync()
