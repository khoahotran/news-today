from datetime import date

def normalize_date_range(
    value: "date | list[date] | tuple[date, ...] | None",
    min_date: date,
    max_date: date
) -> tuple[date, date]:
    """Chuẩn hóa giá trị date_input thành tuple (start_date, end_date)"""
    from collections.abc import Iterable

    if value is None or value == () or value == []:
        return (min_date, max_date)

    if isinstance(value, date):
        return (value, value)

    if isinstance(value, Iterable):
        lst = list(value)
        if len(lst) == 1:
            return (lst[0], lst[0])
        elif len(lst) >= 2:
            return (lst[0], lst[1])

    return (min_date, max_date)
