def safe_int(value, default=None):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
