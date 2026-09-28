from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import ServiceError
from app.models import Application
from app.presenters import application_detail_out, application_out, application_result_out
from app.schemas import ApplicationDetailOut, ApplicationOut, ApplicationResultOut
from app.services.application_service import apply_application

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationOut])
def list_applications(db: Session = Depends(get_db)):
    return [application_out(a) for a in db.query(Application).order_by(Application.id.desc()).all()]


@router.get("/{application_id}", response_model=ApplicationDetailOut)
def get_application(application_id: int, db: Session = Depends(get_db)):
    app = db.get(Application, application_id)
    if app is None:
        raise ServiceError(404, "Application not found")
    return application_detail_out(app)


@router.get("/{application_id}/result", response_model=ApplicationResultOut)
def get_application_result(application_id: int, db: Session = Depends(get_db)):
    app = db.get(Application, application_id)
    if app is None:
        raise ServiceError(404, "Application not found")
    return application_result_out(app)



@router.post("/{application_id}/apply", response_model=ApplicationDetailOut)
def apply(application_id: int, db: Session = Depends(get_db)):
    """Runs synchronously in this skeleton. Move to BackgroundTasks + polling for slow real sites."""
    return application_detail_out(apply_application(db, application_id))
