def convert_seconds_to_minutes_format(seconds: int) -> str:
    seconds_reminder = seconds % 60
    computed_minutes = seconds // 60
    if computed_minutes and seconds_reminder:
        return f"{computed_minutes} min {seconds_reminder} sec"
    if computed_minutes:
        return f"{computed_minutes} min"
    else:
        return f"{seconds} sec"


def test_convert_seconds_to_minutes_format():
    assert convert_seconds_to_minutes_format(seconds=4) == "4 sec"
    assert convert_seconds_to_minutes_format(seconds=120) == "2 min"
    assert convert_seconds_to_minutes_format(seconds=125) == "2 min 5 sec"
