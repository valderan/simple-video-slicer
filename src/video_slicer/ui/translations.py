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
    "file_info_template": Translation(
        "file_info_template",
        "Длительность: {duration} | Разрешение: {resolution} | Кодеки: {codecs}",
        "Duration: {duration} | Resolution: {resolution} | Codecs: {codecs}",
    ),
    "file_info_unknown": Translation(
        "file_info_unknown",
        "нет данных",
        "n/a",
    ),
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
    "settings_menu": Translation("settings_menu", "Настройки", "Settings"),
    "settings_title": Translation("settings_title", "Настройки", "Settings"),
    "settings_language": Translation("settings_language", "Язык", "Language"),
    "settings_theme": Translation("settings_theme", "Тема", "Theme"),
    "settings_ffmpeg": Translation("settings_ffmpeg", "Путь к FFmpeg", "FFmpeg path"),
    "settings_ffmpeg_placeholder": Translation(
        "settings_ffmpeg_placeholder",
        "Оставьте пустым для использования FFmpeg из PATH",
        "Leave empty to use FFmpeg from PATH",
    ),
    "settings_detect_ffmpeg": Translation(
        "settings_detect_ffmpeg",
        "Определить автоматически",
        "Detect automatically",
    ),
    "settings_enable_logging": Translation(
        "settings_enable_logging",
        "Сохранять полный журнал в файл",
        "Save detailed log to file",
    ),
    "settings_log_file": Translation(
        "settings_log_file",
        "Файл журнала",
        "Log file",
    ),
    "theme_light": Translation("theme_light", "Светлая", "Light"),
    "theme_dark": Translation("theme_dark", "Тёмная", "Dark"),
    "help_menu": Translation("help_menu", "Справка", "Help"),
    "help_manual": Translation("help_manual", "Руководство пользователя", "User guide"),
    "help_about": Translation("help_about", "О программе", "About"),
    "help_manual_content": Translation(
        "help_manual_content",
        """
SVS - Simple Video Slicer помогает быстро нарезать видеофайл на отдельные сегменты.

Главное окно:
 • Входной видеофайл – выберите исходное видео. После выбора появится информация о файле.
 • Выходная папка – каталог, куда будут сохраняться готовые сегменты.
 • Таблица сегментов – список всех фрагментов, которые будут вырезаны.
 • Кнопки управления – добавление, редактирование, удаление, дублирование и предпросмотр сегментов.
 • Прогресс и журнал – отображают текущее состояние обработки и сообщения FFmpeg.

Добавление сегментов:
 1. Нажмите «Добавить сегмент».
 2. Укажите время начала и конца. Если конец пустой – сегмент будет до конца файла.
 3. При необходимости задайте имя файла, формат и параметры конвертации.

Обработка:
 • После заполнения списка сегментов нажмите «Запустить обработку».
 • Кнопка «Остановить» прерывает текущий процесс FFmpeg.

Дополнительно:
 • Используйте меню «Настройки» для выбора языка, темы, указания ffmpeg и параметров журнала.
 • Кнопки «Сохранить список» и «Загрузить список» позволяют работать с сегментами в формате JSON.
        """.strip(),
        """
SVS - Simple Video Slicer helps you split a video into separate clips.

Main window:
 • Input video file – choose the source video. File information appears after selection.
 • Output directory – folder where the resulting segments are stored.
 • Segment table – list of all clips to be exported.
 • Control buttons – add, edit, delete, duplicate and preview segments.
 • Progress and log – show the processing state and FFmpeg messages.

Adding segments:
 1. Click "Add segment".
 2. Specify the start and end time. Leave the end empty to cut until the end of the file.
 3. Optionally set a file name, container and conversion parameters.

Processing:
 • After preparing the segment list press "Start processing".
 • The "Stop" button interrupts the current FFmpeg run.

Additional:
 • Use the "Settings" menu to choose language, theme, ffmpeg path and logging options.
 • The "Save list" and "Load list" buttons store and restore segment presets in JSON format.
        """.strip(),
    ),
    "about_text": Translation(
        "about_text",
        "SVS - Simple Video Slicer\nVladimir Kundryukov\nhttps://github.com/valderan/simple-video-slicer",
        "SVS - Simple Video Slicer\nVladimir Kundryukov\nhttps://github.com/valderan/simple-video-slicer",
    ),
    "save_segments": Translation("save_segments", "Сохранить список", "Save list"),
    "load_segments": Translation("load_segments", "Загрузить список", "Load list"),
    "tooltip_save_segments": Translation(
        "tooltip_save_segments",
        "Сохранить сегменты в JSON",
        "Save segments to JSON",
    ),
    "tooltip_load_segments": Translation(
        "tooltip_load_segments",
        "Загрузить сегменты из JSON",
        "Load segments from JSON",
    ),
    "segments_file_filter": Translation(
        "segments_file_filter",
        "JSON файлы (*.json)",
        "JSON files (*.json)",
    ),
    "all_files_filter": Translation(
        "all_files_filter",
        "Все файлы (*)",
        "All files (*)",
    ),
    "segments_save_success": Translation(
        "segments_save_success",
        "Список сегментов сохранён",
        "Segment list saved",
    ),
    "segments_load_success": Translation(
        "segments_load_success",
        "Список сегментов загружен",
        "Segment list loaded",
    ),
    "segments_save_error": Translation(
        "segments_save_error",
        "Не удалось сохранить список сегментов",
        "Failed to save segment list",
    ),
    "segments_load_error": Translation(
        "segments_load_error",
        "Не удалось загрузить список сегментов",
        "Failed to load segment list",
    ),
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
