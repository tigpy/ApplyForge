"""
Jobs Router
"""
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from packages.domain.database import get_db
from packages.domain.models import Job, JobRequirement, JobSource, Candidate, Match
from packages.domain.schemas import JobOut, JobImportRequest, MatchOut
from packages.domain.enums import WorkMode, EmploymentType
from packages.matching.parser import parse_job_requirements
from packages.matching.engine import evaluate_match
from packages.shared.security import SecurityAuditor

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("", response_model=List[JobOut])
def list_jobs(
    source: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    if search:
        query = query.filter(
            (Job.title.ilike(f"%{search}%")) |
            (Job.company.ilike(f"%{search}%")) |
            (Job.location.ilike(f"%{search}%"))
        )
    return query.order_by(Job.discovered_at.desc()).offset(offset).limit(limit).all()

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/import", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def import_job(job_in: JobImportRequest, db: Session = Depends(get_db)):
    # SSRF check
    if job_in.url:
        is_safe, reason = SecurityAuditor.validate_url(job_in.url)
        if not is_safe:
            raise HTTPException(status_code=400, detail=f"Unsafe URL: {reason}")
            
    source = db.query(JobSource).filter(JobSource.name == job_in.source_name).first()
    if not source:
        source = JobSource(name=job_in.source_name, type="manual", configuration={})
        db.add(source)
        db.flush()
        
    ext_id = job_in.external_id or hashlib.sha256(f"{job_in.company}:{job_in.title}:{job_in.description_raw[:100]}".encode()).hexdigest()[:16]
    
    # Check deduplication
    existing = db.query(Job).filter(Job.source_id == source.id, Job.external_id == ext_id).first()
    if existing:
        return existing
        
    job = Job(
        source_id=source.id,
        external_id=ext_id,
        url=job_in.url,
        title=job_in.title,
        company=job_in.company,
        location=job_in.location,
        work_mode=job_in.work_mode,
        employment_type=job_in.employment_type,
        description_raw=job_in.description_raw,
        description_normalized=job_in.description_raw.strip()
    )
    db.add(job)
    db.flush()
    
    # Parse requirements
    parsed_reqs = parse_job_requirements(job_in.description_raw)
    for r in parsed_reqs:
        db.add(JobRequirement(
            job_id=job.id,
            requirement_type=r["requirement_type"],
            text=r["text"],
            normalized_skill=r["normalized_skill"],
            mandatory=r["mandatory"],
            evidence=r["evidence"]
        ))
    db.commit()
    db.refresh(job)
    
    # Run matching
    candidate = db.query(Candidate).first()
    if candidate:
        match_data = evaluate_match(candidate, job)
        match_obj = Match(
            job_id=job.id,
            candidate_id=candidate.id,
            score=match_data["score"],
            required_coverage=match_data["required_coverage"],
            preferred_coverage=match_data["preferred_coverage"],
            explanation=match_data["explanation"],
            hard_gaps=match_data["hard_gaps"],
            strengths=match_data["strengths"],
            uncertainties=match_data["uncertainties"]
        )
        db.add(match_obj)
        db.commit()
        
    return job

@router.post("/{job_id}/match", response_model=MatchOut)
def match_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    candidate = db.query(Candidate).first()
    if not candidate:
        raise HTTPException(status_code=400, detail="Candidate profile required")
        
    match_data = evaluate_match(candidate, job)
    existing_match = db.query(Match).filter(Match.job_id == job.id, Match.candidate_id == candidate.id).first()
    if not existing_match:
        existing_match = Match(
            job_id=job.id,
            candidate_id=candidate.id,
            score=match_data["score"],
            required_coverage=match_data["required_coverage"],
            preferred_coverage=match_data["preferred_coverage"],
            explanation=match_data["explanation"],
            hard_gaps=match_data["hard_gaps"],
            strengths=match_data["strengths"],
            uncertainties=match_data["uncertainties"]
        )
        db.add(existing_match)
    else:
        existing_match.score = match_data["score"]
        existing_match.required_coverage = match_data["required_coverage"]
        existing_match.preferred_coverage = match_data["preferred_coverage"]
        existing_match.explanation = match_data["explanation"]
        existing_match.hard_gaps = match_data["hard_gaps"]
        existing_match.strengths = match_data["strengths"]
        existing_match.uncertainties = match_data["uncertainties"]
        
    db.commit()
    db.refresh(existing_match)
    return existing_match
