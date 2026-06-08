import hashlib


def get_hash(input_string: str | None) -> str:
    if not input_string:
        return ""
    return hashlib.sha256(input_string.encode()).hexdigest()


def convert_seconds_to_minutes_format(seconds: int) -> str:
    seconds_reminder = seconds % 60
    computed_minutes = seconds // 60
    if computed_minutes and seconds_reminder:
        return f"{computed_minutes} min {seconds_reminder} sec"
    if computed_minutes:
        return f"{computed_minutes} min"
    else:
        return f"{seconds} sec"
