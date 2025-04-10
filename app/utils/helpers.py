from datetime import time


def parse_time_string(t: str) -> time:
    return time.fromisoformat(t)
