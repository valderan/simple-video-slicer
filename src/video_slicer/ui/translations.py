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
    "edit_segment": Translation("edit_segment", "Редактировать", "Edit segment"),
    "duplicate_segment": Translation(
        "duplicate_segment", "Дублировать", "Duplicate segment"
    ),
    "process": Translation("process", "Запустить обработку", "Start processing"),
    "stop": Translation("stop", "Остановить", "Stop"),
    "preview": Translation("preview", "Предпросмотр", "Preview"),
    "preview_icon": Translation("preview_icon", "▶", "▶"),
    "video_codec": Translation("video_codec", "Видео кодек", "Video codec"),
    "audio_codec": Translation("audio_codec", "Аудио кодек", "Audio codec"),
    "crf": Translation("crf", "Качество видео (CRF)", "Video quality (CRF)"),
    "extra": Translation(
        "extra",
        "Дополнительные параметры FFmpeg",
        "Additional FFmpeg parameters",
    ),
    "format": Translation("format", "Формат", "Format"),
    "convert": Translation("convert", "Конвертация", "Conversion"),
    "convert_column": Translation("convert_column", "Конвертация", "Conversion"),
    "convert_checkbox": Translation(
        "convert_checkbox",
        "Конвертировать видео",
        "Convert video",
    ),
    "conversion_settings": Translation(
        "conversion_settings",
        "Параметры конвертации",
        "Conversion settings",
    ),
    "help_menu": Translation("help_menu", "Справка", "Help"),
    "help_manual": Translation("help_manual", "Руководство пользователя", "User guide"),
    "language_menu": Translation("language_menu", "Язык", "Language"),
    "language_ru": Translation("language_ru", "Русский", "Russian"),
    "language_en": Translation("language_en", "Английский", "English"),
    "status_ready": Translation("status_ready", "Готово", "Ready"),
    "status_processing": Translation("status_processing", "Обработка...", "Processing..."),
    "status_processing_segment": Translation(
        "status_processing_segment",
        "Обработка фрагмента {current} из {total}: {name}",
        "Processing segment {current} of {total}: {name}",
    ),
    "status_stopped": Translation("status_stopped", "Обработка остановлена", "Processing stopped"),
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
    "yes": Translation("yes", "Да", "Yes"),
    "no": Translation("no", "Нет", "No"),
    "no_segments": Translation(
        "no_segments",
        "Список сегментов пуст",
        "Segment list is empty",
    ),
    "progress_label": Translation("progress_label", "Прогресс:", "Progress:"),
    "progress_idle": Translation("progress_idle", "Готов к запуску", "Waiting"),
    "progress_template": Translation(
        "progress_template",
        "Фрагмент {current} из {total}",
        "Segment {current} of {total}",
    ),
    "log_label": Translation("log_label", "Журнал", "Log"),
    "log_processing_segment": Translation(
        "log_processing_segment",
        "Начата обработка {current}/{total}: {name}",
        "Processing {current}/{total}: {name}",
    ),
    "log_segment_done": Translation(
        "log_segment_done",
        "Завершено: {name}",
        "Completed: {name}",
    ),
    "processing_complete": Translation(
        "processing_complete",
        "Обработка завершена успешно",
        "Processing completed successfully",
    ),
    "processing_stop_requested": Translation(
        "processing_stop_requested",
        "Запрошена остановка обработки",
        "Stop requested",
    ),
    "processing_stop_ack": Translation(
        "processing_stop_ack",
        "Обработка остановлена пользователем",
        "Processing stopped by user",
    ),
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
    "tooltip_edit": Translation(
        "tooltip_edit",
        "Изменить выбранный сегмент",
        "Edit the selected segment",
    ),
    "tooltip_remove": Translation(
        "tooltip_remove",
        "Удалить выбранный сегмент",
        "Remove the selected segment",
    ),
    "tooltip_duplicate": Translation(
        "tooltip_duplicate",
        "Создать копию выбранного сегмента",
        "Duplicate the selected segment",
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
    "tooltip_stop": Translation(
        "tooltip_stop",
        "Прервать текущую обработку",
        "Stop current processing",
    ),
    "filename_placeholder": Translation(
        "filename_placeholder",
        "Оставьте пустым для автоматического имени",
        "Leave blank to auto-generate name",
    ),
    "start_placeholder": Translation(
        "start_placeholder",
        "HH:MM:SS или HH:MM:SS.mmm",
        "HH:MM:SS or HH:MM:SS.mmm",
    ),
    "end_placeholder": Translation(
        "end_placeholder",
        "HH:MM:SS или оставьте пустым",
        "HH:MM:SS or leave empty",
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
