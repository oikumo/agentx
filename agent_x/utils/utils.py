import os


def safe_int(value, default=None):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def clear_console():
    if os.name == "nt":  # Windows
        _ = os.system("cls")
    else:
        _ = os.system("clear")
