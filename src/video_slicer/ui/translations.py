"""Простая система локализации на двух языках."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Translation:
    key: str
    ru: str
    en: str


TRANSLATIONS: Dict[str, Translation] = {
    "file_label": Translation("file_label", "Входной видеофайл:", "Input video file:"),
    "browse": Translation("browse", "Обзор...", "Browse..."),
    "output_label": Translation("output_label", "Выходная папка:", "Output directory:"),
    "segment_table": Translation("segment_table", "Сегменты", "Segments"),
    "add_segment": Translation("add_segment", "Добавить сегмент", "Add segment"),
    "remove_segment": Translation("remove_segment", "Удалить сегмент", "Remove segment"),
    "process": Translation("process", "Запустить обработку", "Process"),
    "preview": Translation("preview", "Предпросмотр", "Preview"),
    "video_codec": Translation("video_codec", "Видео кодек", "Video codec"),
    "audio_codec": Translation("audio_codec", "Аудио кодек", "Audio codec"),
    "crf": Translation("crf", "Качество видео (CRF)", "Video quality (CRF)"),
    "extra": Translation(
        "extra",
        "Дополнительные параметры FFmpeg",
        "Additional FFmpeg parameters",
    ),
    "help_menu": Translation("help_menu", "Справка", "Help"),
    "help_manual": Translation("help_manual", "Руководство пользователя", "User guide"),
    "language_menu": Translation("language_menu", "Язык", "Language"),
    "language_ru": Translation("language_ru", "Русский", "Russian"),
    "language_en": Translation("language_en", "Английский", "English"),
    "status_ready": Translation("status_ready", "Готово", "Ready"),
    "dialog_title": Translation("dialog_title", "Сегмент", "Segment"),
    "start_time": Translation("start_time", "Начало", "Start"),
    "end_time": Translation("end_time", "Конец", "End"),
    "filename": Translation("filename", "Имя файла", "Filename"),
    "ok": Translation("ok", "ОК", "OK"),
    "cancel": Translation("cancel", "Отмена", "Cancel"),
    "preview_title": Translation("preview_title", "Предпросмотр", "Preview"),
    "preview_close": Translation("preview_close", "Закрыть", "Close"),
    "error": Translation("error", "Ошибка", "Error"),
    "info": Translation("info", "Информация", "Info"),
    "tooltip_file": Translation(
        "tooltip_file",
        "Выберите источник видеофайла",
        "Select the source video file",
    ),
    "tooltip_output": Translation(
        "tooltip_output",
        "Каталог, в который будут сохранены сегменты",
        "Directory to store the generated segments",
    ),
    "tooltip_add": Translation(
        "tooltip_add",
        "Добавить новый сегмент",
        "Add a new segment",
    ),
    "tooltip_remove": Translation(
        "tooltip_remove",
        "Удалить выбранный сегмент",
        "Remove the selected segment",
    ),
    "tooltip_preview": Translation(
        "tooltip_preview",
        "Показать миниатюру сегмента",
        "Show segment thumbnail",
    ),
    "tooltip_process": Translation(
        "tooltip_process",
        "Запустить обработку всех сегментов",
        "Start processing all segments",
    ),
}


class Translator:
    """Простая реализация переводчика."""

    def __init__(self, language: str = "ru") -> None:
        if language not in {"ru", "en"}:
            raise ValueError("Поддерживаются только языки 'ru' и 'en'")
        self.language = language

    def set_language(self, language: str) -> None:
        if language not in {"ru", "en"}:
            raise ValueError("Поддерживаются только языки 'ru' и 'en'")
        self.language = language

    def tr(self, key: str) -> str:
        translation = TRANSLATIONS.get(key)
        if not translation:
            return key
        return getattr(translation, self.language)
