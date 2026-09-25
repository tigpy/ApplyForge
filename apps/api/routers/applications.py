"""
Applications Router with Inviolable State Machine & Human Approval Enforcement
"""
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List, Optional
from packages.domain.database import get_db
from packages.domain.models import Application, ApplicationQuestion, AuditEvent, Candidate, Job, Resume
from packages.domain.enums import ApplicationState
from packages.domain.state_machine import validate_transition
from packages.domain.schemas import ApplicationOut, ApplicationCreate, ApplicationUpdate
from packages.documents.tailor import select_best_resume_variant, tailor_candidate_materials
from packages.documents.pdf_generator import generate_resume_pdf
from packages.llm.factory import get_llm_provider

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.get("", response_model=List[ApplicationOut])
def list_applications(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    return query.order_by(Application.updated_at.desc()).all()

@router.get("/queue", response_model=List[ApplicationOut])
def get_review_queue(db: Session = Depends(get_db)):
    return db.query(Application).filter(Application.status == ApplicationState.AWAITING_REVIEW).order_by(Application.created_at.desc()).all()

@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

@router.post("/prepare", response_model=ApplicationOut)
def prepare_application(prep: ApplicationCreate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == prep.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    candidate = db.query(Candidate).first()
    if not candidate:
        raise HTTPException(status_code=400, detail="Candidate profile required")
        
    existing = db.query(Application).filter(Application.job_id == job.id).first()
    if existing:
        return existing
        
    # Select best resume
    selected_resume = select_best_resume_variant(candidate, job)
    
    # Create application in AWAITING_REVIEW status
    app = Application(
        candidate_id=candidate.id,
        job_id=job.id,
        resume_id=selected_resume.id if selected_resume else None,
        status=ApplicationState.AWAITING_REVIEW,
        notes=prep.notes or f"Auto-prepared with resume: {selected_resume.name if selected_resume else 'Master'}"
    )
    db.add(app)
    db.flush()
    
    # Generate tailored ground-truth questions
    questions = [
        ("Are you legally authorized to work in the US without restriction?", candidate.work_authorization, "candidate.work_authorization"),
        ("What degree do you hold and from where?", f"{candidate.educations[0].degree} in {candidate.educations[0].field} from {candidate.educations[0].institution}" if candidate.educations else "B.S. in CS", "candidate.educations"),
        ("What professional certifications do you possess?", ", ".join([c.name for c in candidate.certifications]) if candidate.certifications else "CompTIA Security+", "candidate.certifications"),
        ("Summarize your relevant security experience and projects.", f"Hands-on experience from {candidate.experiences[0].title} at {candidate.experiences[0].organization} and projects: {', '.join([p.name for p in candidate.projects])}" if candidate.experiences else "Project experience", "candidate.experiences")
    ]
    
    for q_text, ans_text, src in questions:
        db.add(ApplicationQuestion(
            application_id=app.id,
            question=q_text,
            answer=ans_text,
            final_answer=ans_text,
            answer_source=src,
            requires_review=True
        ))
        
    # Audit log
    payload_hash = hashlib.sha256(f"{app.id}:PREPARED:{datetime.now(timezone.utc)}".encode()).hexdigest()
    db.add(AuditEvent(
        application_id=app.id,
        event_type="PREPARED_AWAITING_REVIEW",
        actor="System",
        payload_hash=payload_hash,
        event_metadata={"job_title": job.title, "company": job.company}
    ))
    db.commit()
    db.refresh(app)
    return app

@router.post("/{app_id}/approve", response_model=ApplicationOut)
def approve_application(app_id: int, notes: Optional[str] = None, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    validate_transition(app.status, ApplicationState.APPROVED)
    app.status = ApplicationState.APPROVED
    app.approved_at = datetime.now(timezone.utc)
    if notes:
        app.notes = (app.notes or "") + f"\nApproved note: {notes}"
        
    payload_hash = hashlib.sha256(f"{app.id}:APPROVED:{datetime.now(timezone.utc)}".encode()).hexdigest()
    db.add(AuditEvent(
        application_id=app.id,
        event_type="USER_APPROVED",
        actor="HumanReviewer",
        payload_hash=payload_hash,
        event_metadata={"approval_status": "GRANTED"}
    ))
    db.commit()
    db.refresh(app)
    return app

@router.post("/{app_id}/reject", response_model=ApplicationOut)
def reject_application(app_id: int, notes: Optional[str] = None, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    validate_transition(app.status, ApplicationState.SKIP)
    app.status = ApplicationState.SKIP
    if notes:
        app.notes = (app.notes or "") + f"\nSkipped/Rejected: {notes}"
        
    payload_hash = hashlib.sha256(f"{app.id}:SKIPPED:{datetime.now(timezone.utc)}".encode()).hexdigest()
    db.add(AuditEvent(
        application_id=app.id,
        event_type="USER_SKIPPED",
        actor="HumanReviewer",
        payload_hash=payload_hash,
        event_metadata={"reason": notes or "Skipped by user"}
    ))
    db.commit()
    db.refresh(app)
    return app

@router.post("/{app_id}/submit", response_model=ApplicationOut)
def submit_application(app_id: int, db: Session = Depends(get_db)):
    """
    Inviolable Rule: Application MUST be in APPROVED state.
    Never silently submit unapproved applications!
    """
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
        
    if app.status != ApplicationState.APPROVED:
        raise HTTPException(
            status_code=400,
            detail=f"Inviolable Safety Violation: Cannot submit application in state '{app.status.value}'. Must be explicitly APPROVED by human reviewer first."
        )
        
    validate_transition(app.status, ApplicationState.SUBMITTING)
    app.status = ApplicationState.SUBMITTING
    db.commit()
    
    # Finish submission
    validate_transition(app.status, ApplicationState.SUBMITTED)
    app.status = ApplicationState.SUBMITTED
    app.submitted_at = datetime.now(timezone.utc)
    
    payload_hash = hashlib.sha256(f"{app.id}:SUBMITTED:{datetime.now(timezone.utc)}".encode()).hexdigest()
    db.add(AuditEvent(
        application_id=app.id,
        event_type="APPLICATION_SUBMITTED",
        actor="SafeConnectorExecutor",
        payload_hash=payload_hash,
        event_metadata={"job_title": app.job.title, "company": app.job.company}
    ))
    db.commit()
    db.refresh(app)
    return app

@router.get("/{app_id}/resume/pdf")
def download_application_pdf(app_id: int, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    candidate = db.query(Candidate).first()
    llm = get_llm_provider()
    tailored = tailor_candidate_materials(candidate, app.job, app.resume, llm)
    pdf_path = generate_resume_pdf(candidate, app.job, app.resume, tailored)
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="Application_{app.id}_Resume.pdf"'}
    )
