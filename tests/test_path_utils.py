from pathlib import Path

import pytest

from video_slicer.utils import path_utils


def test_format_for_display_windows_drive():
    value = "C:/Users/test/My Videos/sample.mp4"
    assert (
        path_utils.format_for_display(value)
        == "C:\\Users\\test\\My Videos\\sample.mp4"
    )


def test_format_for_display_unc_path():
    value = r"\\Server\Share\folder/video.mp4"
    assert path_utils.format_for_display(value) == r"\\Server\Share\folder\video.mp4"


def test_format_for_display_posix(tmp_path):
    path = tmp_path / "clip.mkv"
    assert path_utils.format_for_display(path) == str(path)


def test_format_for_logging_windows_drive():
    value = "C:/Users/test/My Videos/sample.mp4"
    normalized = path_utils.normalize_user_path(value)
    expected = f'"{normalized.replace("\\", "\\\\")}"'
    assert path_utils.format_for_logging(value) == expected


def test_format_for_logging_posix(tmp_path):
    path = tmp_path / "clip.mkv"
    assert path_utils.format_for_logging(path) == f'"{path}"'


def test_format_for_logging_none():
    assert path_utils.format_for_logging(None) == '""'


def test_normalize_user_path_strips_quotes_and_whitespace():
    raw = '   "C:/Tools/ffmpeg/bin/ffmpeg.exe"   '
    expected = "C:\\Tools\\ffmpeg\\bin\\ffmpeg.exe"
    assert path_utils.normalize_user_path(raw) == expected


@pytest.mark.parametrize("value", ["", "   ", None])
def test_normalize_user_path_empty_values(value):
    assert path_utils.normalize_user_path(value) is None


def test_normalize_user_path_expands_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    path = path_utils.normalize_user_path("~/video.mp4")
    assert path == str(Path(tmp_path, "video.mp4"))
