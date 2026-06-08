from src.utils import convert_seconds_to_minutes_format


def test_convert_seconds_to_minutes_format():
    assert convert_seconds_to_minutes_format(seconds=4) == "4 sec"
    assert convert_seconds_to_minutes_format(seconds=120) == "2 min"
    assert convert_seconds_to_minutes_format(seconds=125) == "2 min 5 sec"
