from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)


class Database(object):
    def __init__(self):
        pass

    def __enter__(self):
        self.db = SessionLocal()
        return self.db

    def __exit__(self, *args, **kwargs):
        self.db.close()
