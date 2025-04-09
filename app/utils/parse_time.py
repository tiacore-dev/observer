from datetime import datetime, time


def parse_time(time_input):
    """
    Парсит строку или объект времени в объект time, поддерживая форматы с и без секунд.
    """
    if isinstance(time_input, time):  # Используем правильный тип datetime.time
        return time_input  # Если это уже объект time, возвращаем его

    if isinstance(time_input, str):  # Если это строка, пытаемся распарсить
        for fmt in ('%H:%M', '%H:%M:%S'):
            try:
                return datetime.strptime(time_input, fmt).time()
            except ValueError:
                continue

    raise ValueError(f"Некорректный формат времени: {time_input}")
