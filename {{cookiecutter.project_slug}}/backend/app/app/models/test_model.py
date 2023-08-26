from __future__ import annotations

from app.db.base_class import Base
from app.utils.base import default_ns_id
from sqlalchemy import Column, BigInteger

from app.db.base_class import BaseModelManager


class TestModel(Base):
    id = Column(BigInteger, primary_key=True, default=default_ns_id)

    class Manager(BaseModelManager):
        pass

    @classmethod
    def objects(cls, db=None) -> Manager:
        return cls.create_objects_manager(cls.Manager, db=db)
