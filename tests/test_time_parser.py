from video_slicer.utils.time_parser import parse_time, format_time


def test_parse_time_formats():
    assert parse_time("00:00:05") == 5
    assert parse_time("01:02:03.500") == 3723.5
    assert parse_time("02:03") == 123
    assert parse_time("45") == 45


def test_format_time_roundtrip():
    value = 123.456
    assert parse_time(format_time(value)) == 123.456
