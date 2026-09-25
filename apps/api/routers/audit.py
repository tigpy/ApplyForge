"""
Audit Events Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from packages.domain.database import get_db
from packages.domain.models import AuditEvent
from packages.domain.schemas import AuditEventOut

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/logs", response_model=List[AuditEventOut])
def get_audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
