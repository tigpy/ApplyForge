"""
Resume Variants Router
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List
from packages.domain.database import get_db
from packages.domain.models import Candidate, Job, Resume
from packages.domain.schemas import ResumeOut, ResumeCreate
from packages.documents.pdf_generator import generate_resume_pdf
from packages.documents.tailor import tailor_candidate_materials
from packages.llm.factory import get_llm_provider

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.get("/variants", response_model=List[ResumeOut])
def list_resume_variants(db: Session = Depends(get_db)):
    return db.query(Resume).all()

@router.post("/variants", response_model=ResumeOut)
def create_resume_variant(variant_in: ResumeCreate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).first()
    if not candidate:
        raise HTTPException(status_code=400, detail="Candidate profile required")
    res = Resume(candidate_id=candidate.id, **variant_in.model_dump())
    db.add(res)
    db.commit()
    db.refresh(res)
    return res

@router.get("/variants/{variant_id}", response_model=ResumeOut)
def get_resume_variant(variant_id: int, db: Session = Depends(get_db)):
    res = db.query(Resume).filter(Resume.id == variant_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resume not found")
    return res

@router.get("/variants/{variant_id}/pdf")
def download_resume_pdf(variant_id: int, db: Session = Depends(get_db)):
    res = db.query(Resume).filter(Resume.id == variant_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resume not found")
    candidate = db.query(Candidate).first()
    dummy_job = Job(title=res.job_family, company="General Application", location="Remote", description_raw="")
    llm = get_llm_provider()
    tailored = tailor_candidate_materials(candidate, dummy_job, res, llm)
    pdf_path = generate_resume_pdf(candidate, dummy_job, res, tailored)
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{res.name.replace(" ", "_")}.pdf"'}
    )
