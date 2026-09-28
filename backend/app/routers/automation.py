from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.api import AutomationRunRequest, AutomationRunResult
from app.services.automation_service import AutomationService

router = APIRouter(prefix="/automation", tags=["automation"])


@router.post("/run", response_model=AutomationRunResult)
def run_automation(body: AutomationRunRequest | None = None, db: Session = Depends(get_db)):
    body = body or AutomationRunRequest()
    try:
        service = AutomationService(db)
        return service.run_job_search(
            connector_name=body.connector, query=body.query, auto_apply=body.auto_apply
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Automation run error: {exc}") from exc
