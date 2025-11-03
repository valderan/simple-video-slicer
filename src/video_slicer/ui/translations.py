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
    "metadata_button": Translation("metadata_button", "Метаинфо", "Metadata"),
    "metadata_tooltip": Translation(
        "metadata_tooltip",
        "Показать подробную метаинформацию файла",
        "Show detailed file metadata",
    ),
    "segment_metadata_column": Translation(
        "segment_metadata_column",
        "Метаинфо",
        "Metadata",
    ),
    "segment_metadata_tooltip": Translation(
        "segment_metadata_tooltip",
        "Показать метаинформацию созданного сегмента",
        "Show metadata of the exported segment",
    ),
    "segment_metadata_dialog_title": Translation(
        "segment_metadata_dialog_title",
        "Метаинформация сегмента",
        "Segment metadata",
    ),
    "segment_metadata_file_label": Translation(
        "segment_metadata_file_label",
        "Файл сегмента: {path}",
        "Segment file: {path}",
    ),
    "segment_metadata_error": Translation(
        "segment_metadata_error",
        "Не удалось получить метаинформацию: {error}",
        "Failed to load metadata: {error}",
    ),
    "segment_metadata_missing": Translation(
        "segment_metadata_missing",
        "Файл сегмента не найден",
        "Segment file not found",
    ),
    "metadata_dialog_title": Translation(
        "metadata_dialog_title",
        "Метаинформация файла",
        "File metadata",
    ),
    "metadata_file_label": Translation(
        "metadata_file_label",
        "Файл: {path}",
        "File: {path}",
    ),
    "metadata_not_available": Translation(
        "metadata_not_available",
        "Метаинформация недоступна",
        "Metadata is not available",
    ),
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
    "extra_hint": Translation(
        "extra_hint",
        "Например: -preset slow -profile:v high",
        "For example: -preset slow -profile:v high",
    ),
    "format": Translation("format", "Формат", "Format"),
    "convert": Translation("convert", "Конвертация", "Conversion"),
    "convert_column": Translation("convert_column", "Конвертация", "Conversion"),
    "convert_checkbox": Translation(
        "convert_checkbox",
        "Конвертировать видео",
        "Convert video",
    ),
    "remove_audio_label": Translation("remove_audio_label", "Аудио", "Audio"),
    "remove_audio_checkbox": Translation(
        "remove_audio_checkbox",
        "Удалить аудиодорожку",
        "Remove audio track",
    ),
    "conversion_settings": Translation(
        "conversion_settings",
        "Параметры конвертации",
        "Conversion settings",
    ),
    "main_menu": Translation("main_menu", "Меню", "Menu"),
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
    "settings_strip_metadata": Translation(
        "settings_strip_metadata",
        "Стирать метаинформацию в сегментах",
        "Strip metadata from generated segments",
    ),
    "settings_embed_metadata": Translation(
        "settings_embed_metadata",
        "Добавлять информацию о SVS в метаинформацию файла",
        "Embed SVS information into file metadata",
    ),
    "settings_use_icons": Translation(
        "settings_use_icons",
        "Использовать иконки вместо надписей",
        "Use icons instead of button labels",
    ),
    "theme_light": Translation("theme_light", "Светлая", "Light"),
    "theme_dark": Translation("theme_dark", "Тёмная", "Dark"),
    "help_manual": Translation("help_manual", "Руководство пользователя", "User guide"),
    "help_about": Translation("help_about", "О программе", "About"),
    "menu_download_ffmpeg": Translation(
        "menu_download_ffmpeg", "Скачать FFmpeg", "Download FFmpeg"
    ),
    "help_manual_content": Translation(
        "help_manual_content",
        """
SVS - Simple Video Slicer помогает быстро нарезать видеофайл на отдельные сегменты.

Главное окно:
 • Входной видеофайл – выберите исходное видео. После выбора появится информация о файле.
 • Выходная папка – каталог, куда будут сохраняться готовые сегменты.
 • Таблица сегментов – список всех фрагментов, которые будут вырезаны.
 • Кнопки управления – добавление, редактирование, удаление и дублирование сегментов.
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
 • Control buttons – add, edit, delete and duplicate segments.
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
    "about_version": Translation(
        "about_version", "Версия {version}", "Version {version}"
    ),
    "about_author": Translation(
        "about_author", "Автор: {name}", "Author: {name}"
    ),
    "about_repo": Translation(
        "about_repo",
        "© {year} <a href=\"{url}\">{url}</a>",
        "© {year} <a href=\"{url}\">{url}</a>",
    ),
    "about_description": Translation(
        "about_description",
        (
            "Современный инструмент для точной нарезки и подготовки видеоконтента."
            " Поддерживает конвертацию, предпросмотр и экспорт пользовательских списков"
            " сегментов."
        ),
        (
            "A polished tool for precise video slicing and preparation."
            " Includes conversion, preview, and reusable segment playlists."
        ),
    ),
    "about_tagline": Translation(
        "about_tagline",
        "Создавайте идеальные клипы за считанные минуты",
        "Create perfect clips in minutes",
    ),
    "save_segments": Translation("save_segments", "Сохранить список", "Save list"),
    "load_segments": Translation("load_segments", "Загрузить список", "Load list"),
    "bulk_create_button": Translation(
        "bulk_create_button", "Создать список", "Create list"
    ),
    "bulk_create_tooltip": Translation(
        "bulk_create_tooltip",
        "Создать сегменты по текстовому описанию",
        "Generate segments from a text description",
    ),
    "clear_segments": Translation(
        "clear_segments",
        "Очистить список",
        "Clear list",
    ),
    "tooltip_clear_segments": Translation(
        "tooltip_clear_segments",
        "Удалить все сегменты",
        "Remove all segments",
    ),
    "bulk_edit_segments": Translation(
        "bulk_edit_segments",
        "Применить к выбранным",
        "Apply to selected",
    ),
    "tooltip_bulk_edit": Translation(
        "tooltip_bulk_edit",
        "Изменить формат и параметры конвертации выбранных сегментов",
        "Change format and conversion settings for selected segments",
    ),
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
    "bulk_create_title": Translation(
        "bulk_create_title",
        "Создать список сегментов",
        "Create segment list",
    ),
    "bulk_create_description": Translation(
        "bulk_create_description",
        (
            "<p>Введите список сегментов, по одному в строке:</p>"
            "<ul>"
            "<li><b>Время</b> указывается в формате HH:MM:SS, MM:SS или SS.</li>"
            "<li>После времени можно добавить название через тире, пробел или оставить"
            " только время для автоматического имени.</li>"
            "<li>Строки должны быть расположены по возрастанию времени.</li>"
            "</ul>"
        ),
        (
            "<p>Enter the list of segments, one per line:</p>"
            "<ul>"
            "<li><b>Time</b> can be formatted as HH:MM:SS, MM:SS or SS.</li>"
            "<li>Add the title after the time with a dash, a space, or leave only the"
            " time to auto-generate a name.</li>"
            "<li>Lines must be sorted in ascending order of time.</li>"
            "</ul>"
        ),
    ),
    "bulk_create_placeholder": Translation(
        "bulk_create_placeholder",
        "0:00 - Введение\n0:30 - Основная часть\n1:45 - Завершение",
        "0:00 - Introduction\n0:30 - Main part\n1:45 - Wrap-up",
    ),
    "bulk_create_error_empty": Translation(
        "bulk_create_error_empty",
        "Введите хотя бы одну строку",
        "Enter at least one line",
    ),
    "bulk_create_error_format": Translation(
        "bulk_create_error_format",
        "Строка {line} должна начинаться со времени",
        "Line {line} must start with a time value",
    ),
    "bulk_create_error_title": Translation(
        "bulk_create_error_title",
        "Строка {line} не содержит названия сегмента",
        "Line {line} is missing the segment title",
    ),
    "bulk_create_error_time": Translation(
        "bulk_create_error_time",
        "Некорректное время в строке {line}",
        "Invalid time value on line {line}",
    ),
    "bulk_create_error_order": Translation(
        "bulk_create_error_order",
        "Время в строке {line} должно быть больше предыдущего",
        "Time on line {line} must be greater than the previous one",
    ),
    "bulk_create_error_negative": Translation(
        "bulk_create_error_negative",
        "Время в строке {line} не может быть отрицательным",
        "Time on line {line} cannot be negative",
    ),
    "bulk_create_error_over_duration": Translation(
        "bulk_create_error_over_duration",
        "Время в строке {line} выходит за пределы длительности видео",
        "Time on line {line} exceeds the video duration",
    ),
    "bulk_create_error_last_segment": Translation(
        "bulk_create_error_last_segment",
        "Последний сегмент не может начинаться у конца видео",
        "The last segment cannot start at the end of the video",
    ),
    "bulk_create_no_file": Translation(
        "bulk_create_no_file",
        "Сначала выберите входной видеофайл",
        "Select an input video file first",
    ),
    "bulk_create_confirm_title": Translation(
        "bulk_create_confirm_title",
        "Создать сегменты по списку",
        "Create segments from list",
    ),
    "bulk_create_confirm_text": Translation(
        "bulk_create_confirm_text",
        "Будет создано сегментов: {count}. Продолжить?",
        "Segments to create: {count}. Continue?",
    ),
    "bulk_create_log": Translation(
        "bulk_create_log",
        "Сегменты созданы из списка ({count}).",
        "Segments created from text list ({count}).",
    ),
    "bulk_create_status": Translation(
        "bulk_create_status",
        "Готово: создано сегментов — {count}",
        "Done: {count} segments created",
    ),
    "bulk_create_option_numbering": Translation(
        "bulk_create_option_numbering",
        "Добавлять нумерацию в начале имени файла",
        "Add numbering at the beginning of filenames",
    ),
    "bulk_create_option_description": Translation(
        "bulk_create_option_description",
        "Включать описание в имена файлов",
        "Include description in filenames",
    ),
    "bulk_create_separator_label": Translation(
        "bulk_create_separator_label",
        "Разделитель:",
        "Separator:",
    ),
    "bulk_create_separator_placeholder": Translation(
        "bulk_create_separator_placeholder",
        "Например: _ или .",
        "For example: _ or .",
    ),
    "bulk_create_separator_error": Translation(
        "bulk_create_separator_error",
        "Разделитель не должен содержать символы \\ / : * ? \" < > |",
        "Separator cannot contain the characters \\ / : * ? \" < > |",
    ),
    "language_menu": Translation("language_menu", "Язык", "Language"),
    "language_ru": Translation("language_ru", "Русский", "Russian"),
    "language_en": Translation("language_en", "Английский", "English"),
    "status_ready": Translation("status_ready", "Готово", "Ready"),
    "status_ffmpeg_missing": Translation(
        "status_ffmpeg_missing",
        "FFmpeg не найден — укажите путь в настройках",
        "FFmpeg not found — configure the path in settings",
    ),
    "status_processing": Translation("status_processing", "Обработка...", "Processing..."),
    "status_processing_segment": Translation(
        "status_processing_segment",
        "Обработка фрагмента {current} из {total}: {name}",
        "Processing segment {current} of {total}: {name}",
    ),
    "status_stopped": Translation("status_stopped", "Обработка остановлена", "Processing stopped"),
    "dialog_title": Translation("dialog_title", "Сегмент", "Segment"),
    "batch_edit_title": Translation(
        "batch_edit_title",
        "Применить настройки к сегментам",
        "Apply settings to segments",
    ),
    "start_time": Translation("start_time", "Начало", "Start"),
    "end_time": Translation("end_time", "Конец", "End"),
    "log_ffmpeg_missing": Translation(
        "log_ffmpeg_missing",
        "FFmpeg не обнаружен. Укажите путь в настройках приложения.",
        "FFmpeg is missing. Please configure it in the settings.",
    ),
    "log_ffmpeg_ready": Translation(
        "log_ffmpeg_ready",
        "FFmpeg найден. Все функции разблокированы.",
        "FFmpeg detected. All features are unlocked.",
    ),
    "chapters_detected_title": Translation(
        "chapters_detected_title",
        "Обнаружены главы видео",
        "Video chapters detected",
    ),
    "chapters_detected_text": Translation(
        "chapters_detected_text",
        "Найдено меток: {count}. Создать сегменты автоматически?",
        "Detected {count} chapter markers. Create segments automatically?",
    ),
    "chapters_replace_question": Translation(
        "chapters_replace_question",
        "Текущий список сегментов будет заменён.",
        "The existing segment list will be replaced.",
    ),
    "chapters_until_end": Translation(
        "chapters_until_end",
        "до конца файла",
        "until end of file",
    ),
    "chapters_created": Translation(
        "chapters_created",
        "Сегменты созданы из меток ({count}).",
        "Segments created from chapter markers ({count}).",
    ),
    "chapters_created_status": Translation(
        "chapters_created_status",
        "Готово: создано сегментов — {count}",
        "Done: {count} segments created",
    ),
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
    "log_copy_success": Translation(
        "log_copy_success",
        "Журнал скопирован в буфер обмена",
        "Log copied to clipboard",
    ),
    "bulk_edit_log": Translation(
        "bulk_edit_log",
        "Параметры применены к сегментам: {count}",
        "Applied settings to segments: {count}",
    ),
    "segments_cleared_log": Translation(
        "segments_cleared_log",
        "Список сегментов очищен",
        "Segment list cleared",
    ),
    "confirm_remove_segments_title": Translation(
        "confirm_remove_segments_title",
        "Удалить сегменты",
        "Delete segments",
    ),
    "confirm_remove_segments_text": Translation(
        "confirm_remove_segments_text",
        "Будут удалены выбранные сегменты ({count}). Продолжить?",
        "Remove the selected segments ({count})?",
    ),
    "confirm_clear_segments_title": Translation(
        "confirm_clear_segments_title",
        "Очистить список",
        "Clear list",
    ),
    "confirm_clear_segments_text": Translation(
        "confirm_clear_segments_text",
        "Удалить все сегменты из списка?",
        "Remove all segments from the list?",
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
    "copy_log": Translation("copy_log", "Копировать журнал", "Copy log"),
    "tooltip_copy_log": Translation(
        "tooltip_copy_log",
        "Скопировать содержимое журнала в буфер обмена",
        "Copy log contents to clipboard",
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
