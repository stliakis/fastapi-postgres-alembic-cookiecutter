from app.utils.base import anything_to_date


class FromDate(object):
    def __call__(self, from_date: str = None):
        return anything_to_date(from_date)


class ToDate(object):
    def __call__(self, to_date: str = None):
        return anything_to_date(to_date)
