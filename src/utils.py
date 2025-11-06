# src/utils.py

import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def get_previous_month_str() -> str:
    """
    Retorna o mês anterior no formato YYYY-MM.
    Ex: se hoje é 2025-11-05 -> retorna '2025-10'
    """
    today = datetime.today()
    previous_month = today - relativedelta(months=1)
    return previous_month.strftime("%Y-%m")

def get_days_in_month(month_str: str) -> int:
    """
    Recebe 'YYYY-MM' e devolve a quantidade de dias daquele mês.
    """
    year, month = map(int, month_str.split("-"))
    first_day = datetime(year, month, 1)
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)
    return (next_month - first_day).days
