from app.db.session import SessionLocal


def get_session():
    return SessionLocal()
