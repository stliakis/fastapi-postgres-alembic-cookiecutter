from typing import Generator
from app.db.session import SessionLocal
from app.utils.lists import PaginationParams


def get_database() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class GetPaginationParams(object):
    def __call__(self, per_page: int = 30, page: int = 1) -> PaginationParams:
        return PaginationParams(per_page=per_page, page=page)
