from datetime import datetime


def log(text):
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now()}] {text}\n"
        )