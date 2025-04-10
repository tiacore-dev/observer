from prometheus_client import Counter

analysis_success_total = Counter(
    "analysis_success_total",
    "Успешные запуски анализа",
    ["chat_id", "schedule_id"]
)

analysis_failed_total = Counter(
    "analysis_failed_total",
    "Проваленные запуски анализа",
    ["chat_id", "schedule_id"]
)
