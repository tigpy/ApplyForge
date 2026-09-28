from fastapi import APIRouter, Depends, File, Form, Response, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas import ResumeOut
from app.services.resume_service import ResumeRepository, ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db)):
    return ResumeRepository(db).list()


@router.post("/upload", response_model=ResumeOut, status_code=201)
def upload_resume(
    file: UploadFile = File(...), display_name: str = Form(""), tags: str = Form(""),
    target_role: str = Form(""), db: Session = Depends(get_db),
):
    data = file.file.read(settings.max_upload_mb * 1024 * 1024 + 1)  # bounded read
    return ResumeService(db).save_upload(file.filename or "resume.pdf", data, display_name, tags, target_role)


@router.delete("/{resume_id}", status_code=204)
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    ResumeService(db).delete(resume_id)
    return Response(status_code=204)
