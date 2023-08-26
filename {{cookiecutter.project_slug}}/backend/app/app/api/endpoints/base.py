from typing import Any

from app.api import deps
from app.models import TestModel
from fastapi import APIRouter, Depends

from app.utils.logging import log
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/test")
def test(db: Session = Depends(deps.get_database)) -> Any:
    log("info", "called test")

    test_model = TestModel()
    test_model.flush(db)

    return {
        "test_object": test_model.id
    }
