from datetime import datetime, timezone
from typing import Literal


def get_today_date() -> str:
    """Возвращает текущую дату в формате 'YYYY-MM-DD'."""
    return datetime.now().strftime('%Y-%m-%d')

def get_current_date_iso(type: str = Literal['start', 'end']):
    if type == 'start':
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT00:00:00Z')
    elif type == 'end':
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT23:59:59Z')
    return None
