from datetime import datetime, timezone, timedelta

from flask import request, g
from sqlalchemy import func, text

from models import db

# Offset по умолчанию: Москва UTC+3
DEFAULT_OFFSET_MINUTES = 180
MAX_OFFSET_MINUTES = 14 * 60      # +14:00
MIN_OFFSET_MINUTES = -12 * 60     # -12:00


def _parse_offset(value):
    if not value:
        return None
    v = value.strip()
    if v.upper().startswith("UTC"):
        v = v[3:]
    try:
        minutes = int(v)
    except ValueError:
        return None
    if not (MIN_OFFSET_MINUTES <= minutes <= MAX_OFFSET_MINUTES):
        return None
    return minutes


def get_user_offset_minutes():
    """Приоритет: X-Timezone → cookie tz_offset → UTC+3."""
    if "tz_offset" in g:
        return g.tz_offset

    offset = _parse_offset(request.headers.get("X-Timezone"))
    if offset is None:
        offset = _parse_offset(request.cookies.get("tz_offset"))
    if offset is None:
        offset = DEFAULT_OFFSET_MINUTES

    g.tz_offset = offset
    return offset


def get_user_tz():
    return timezone(timedelta(minutes=get_user_offset_minutes()))


def _ensure_aware(dt):
    """SQLite хранит naive datetime — считаем, что это UTC."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def to_user_tz(dt):
    if dt is None:
        return None
    return _ensure_aware(dt).astimezone(get_user_tz())


def format_user_dt(dt, fmt="%Y-%m-%d %H:%M"):
    if dt is None:
        return ""
    return to_user_tz(dt).strftime(fmt)


def user_now():
    return datetime.now(get_user_tz())


def user_today_str():
    return user_now().strftime("%Y-%m-%d")


def user_current_month_str():
    return user_now().strftime("%Y-%m")


def user_input_to_utc_naive(date_obj, time_str=None):
    """date + 'ЧЧ:ММ' (локально) -> naive UTC для записи в БД."""
    if time_str:
        try:
            hh, mm = map(int, time_str.split(":"))
            if not (0 <= hh < 24 and 0 <= mm < 60):
                raise ValueError
        except (ValueError, AttributeError):
            hh, mm = 0, 0
    else:
        now = user_now()
        hh, mm = now.hour, now.minute

    local_dt = datetime(
        date_obj.year, date_obj.month, date_obj.day, hh, mm,
        tzinfo=get_user_tz(),
    )
    return local_dt.astimezone(timezone.utc).replace(tzinfo=None)


def utc_naive_to_user_input(dt):
    """naive UTC -> (date, 'ЧЧ:ММ') для предзаполнения формы."""
    if dt is None:
        return None, ""
    aware = _ensure_aware(dt).astimezone(get_user_tz())
    return aware.date(), aware.strftime("%H:%M")


def shifted_month_expr(column, offset_minutes):
    """SQL-выражение 'YYYY-MM' с учётом смещения пользователя."""
    dialect = db.engine.dialect.name
    sign = "+" if offset_minutes >= 0 else "-"
    delta = f"{sign}{abs(offset_minutes)} minutes"

    if dialect == "postgresql":
        return func.to_char(
            func.timezone(text(f"'{delta}'"), column), "YYYY-MM"
        )
    return func.strftime(
        "%Y-%m", func.datetime(column, text(f"'{delta}'"))
    )