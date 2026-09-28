from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CandidateProfile
from app.schemas import ProfileIn, ProfileOut

router = APIRouter(prefix="/profile", tags=["profile"])


def _get_or_create(db: Session) -> CandidateProfile:
    profile = db.get(CandidateProfile, 1)
    if profile is None:
        profile = CandidateProfile(id=1)
        db.add(profile)
        db.commit()
    return profile


@router.get("", response_model=ProfileOut)
def get_profile(db: Session = Depends(get_db)):
    return _get_or_create(db)


@router.put("", response_model=ProfileOut)
def put_profile(body: ProfileIn, db: Session = Depends(get_db)):
    profile = _get_or_create(db)
    for key, value in body.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    return profile
