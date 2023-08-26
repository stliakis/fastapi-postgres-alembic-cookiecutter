from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_fixed

from app.config import settings
from app.db.session import SessionLocal
from app.utils.logging import log

max_tries = 60 * 5
wait_seconds = 1


def main() -> None:
    log("info", "Initializing service")
    init()
    log("info", "Service finished initializing")

    log("info", "App environment: %s" % settings.ENVIRONMENT)
    log("info", "App service: %s" % settings.SERVICE)


@retry(stop=stop_after_attempt(max_tries), wait=wait_fixed(wait_seconds))
def init() -> Session:
    try:
        db = SessionLocal()
        # Try to create session to check if DB is awake
        db.execute("SELECT 1")
        return db
    except Exception as e:
        log("error", str(e))
        raise e


if __name__ == "__main__":
    main()
