import time

def current_time_ms() -> int:
    """
    Returns the current time in milliseconds.
    :return: integer (ms).
    """
    return round(time.time_ns() / 1000000)

def sleep_ms(ms: int) -> None:
    """
    Sleep specified number of milliseconds.

    :param ms: The number of milliseconds to sleep.
    :return: None
    """
    time.sleep(float(ms) / 1000.0)
