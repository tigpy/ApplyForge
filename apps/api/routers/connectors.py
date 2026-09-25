"""
Connectors and Discovery Router
"""
import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from packages.domain.database import get_db
from packages.domain.models import Job, JobRequirement, JobSource, Candidate, Match
from packages.domain.schemas import JobSourceOut
from packages.connectors.registry import connector_registry
from packages.matching.parser import parse_job_requirements
from packages.matching.engine import evaluate_match

router = APIRouter(prefix="/connectors", tags=["Connectors"])

@router.get("/sources", response_model=List[JobSourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(JobSource).all()

@router.post("/discover")
def trigger_discovery(platform: str = "mock", db: Session = Depends(get_db)):
    try:
        connector = connector_registry.get(platform)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    source = db.query(JobSource).filter(JobSource.name == platform).first()
    if not source:
        source = JobSource(name=platform, type=platform, configuration={})
        db.add(source)
        db.flush()
        
    raw_jobs = connector.search(query="cybersecurity OR python")
    candidate = db.query(Candidate).first()
    
    created_count = 0
    for raw in raw_jobs:
        normalized = connector.normalize(raw)
        ext_id = normalized.get("external_id")
        
        exists = db.query(Job).filter(Job.source_id == source.id, Job.external_id == ext_id).first()
        if not exists:
            job = Job(
                source_id=source.id,
                external_id=ext_id,
                url=normalized.get("url"),
                title=normalized.get("title"),
                company=normalized.get("company"),
                location=normalized.get("location"),
                work_mode=normalized.get("work_mode"),
                employment_type=normalized.get("employment_type"),
                description_raw=normalized.get("description_raw"),
                description_normalized=normalized.get("description_normalized")
            )
            db.add(job)
            db.flush()
            
            # Parse requirements
            parsed = parse_job_requirements(job.description_raw)
            for r in parsed:
                db.add(JobRequirement(
                    job_id=job.id,
                    requirement_type=r["requirement_type"],
                    text=r["text"],
                    normalized_skill=r["normalized_skill"],
                    mandatory=r["mandatory"],
                    evidence=r["evidence"]
                ))
            db.flush()
            
            if candidate:
                m_data = evaluate_match(candidate, job)
                db.add(Match(
                    job_id=job.id,
                    candidate_id=candidate.id,
                    score=m_data["score"],
                    required_coverage=m_data["required_coverage"],
                    preferred_coverage=m_data["preferred_coverage"],
                    explanation=m_data["explanation"],
                    hard_gaps=m_data["hard_gaps"],
                    strengths=m_data["strengths"],
                    uncertainties=m_data["uncertainties"]
                ))
            created_count += 1
            
    db.commit()
    return {"status": "success", "platform": platform, "discovered": len(raw_jobs), "new_imported": created_count}
