USER_ROLE:  str = 'user'
LLM_ROLE:   str = 'assistant'
from datetime import datetime, timezone


MONTH_LABELS: list[str] = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def shift_month(year: int, month: int, offset: int) -> tuple[int, int]:
    """Return (year, month) with month in 1-12 after applying offset."""
    index = (year * 12 + (month - 1)) + offset
    return index // 12, (index % 12) + 1


def get_rolling_year_months(months: int) -> list[tuple[int, int]]:
    now = datetime.now(tz=timezone.utc)
    current_year = now.year
    current_month = now.month

    return [
        shift_month(current_year, current_month, offset - (months - 1))
        for offset in range(months)
    ]
