import re


def validate_channel(channel):
    return bool(
        re.match(r"^@[A-Za-z0-9_]{5,}$", channel)
    )
