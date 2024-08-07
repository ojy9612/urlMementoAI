from datetime import datetime, timezone, timedelta


def default_timezone() -> timezone:
    return timezone(timedelta(hours=9))


def datetime_now_timezone(tz: timezone = default_timezone()) -> datetime:
    return datetime.now(tz)


def datetime_to_str(dt: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    return dt.strftime(format)


def str_to_datetime(date_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    return datetime.strptime(date_str, format)
