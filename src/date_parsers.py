from datetime import datetime, timedelta


def custom_knmi_date_parser(hours: str) -> str:
    return datetime.fromtimestamp(1554109200) + timedelta(hours=int(hours))


def knmi_date_parser() -> str:
    # TODO
    pass


def factoryzero_date_parser(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp)


def date_parser(date) -> str:
    return custom_knmi_date_parser(date)
