"""
Candidate Profile Router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from packages.domain.database import get_db
from packages.domain.models import Candidate, Skill
from packages.domain.schemas import CandidateOut, CandidateUpdate, SkillCreate, SkillOut

router = APIRouter(prefix="/candidate", tags=["Candidate"])

@router.get("/profile", response_model=CandidateOut)
def get_candidate_profile(db: Session = Depends(get_db)):
    candidate = db.query(Candidate).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return candidate

@router.put("/profile", response_model=CandidateOut)
def update_candidate_profile(update_data: CandidateUpdate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    for field, val in update_data.model_dump(exclude_unset=True).items():
        setattr(candidate, field, val)
    db.commit()
    db.refresh(candidate)
    return candidate

@router.post("/skills", response_model=SkillOut, status_code=status.HTTP_201_CREATED)
def add_candidate_skill(skill_in: SkillCreate, db: Session = Depends(get_db)):
    candidate = db.query(Candidate).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    skill = Skill(candidate_id=candidate.id, **skill_in.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill

@router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    db.delete(skill)
    db.commit()
    return None
