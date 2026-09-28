import pytest

from app.errors import ServiceError
from app.models import Application, ApplicationStatus as S, Job
from app.services.application_service import can_transition, transition


def test_transition_table():
    assert can_transition(S.ELIGIBLE, S.QUEUED)
    assert can_transition(S.APPLYING, S.APPLIED)
    assert not can_transition(S.APPLIED, S.QUEUED)  # terminal
    assert not can_transition(S.QUEUED, S.APPLIED)  # must pass through APPLYING
    assert not can_transition(S.DUPLICATE, S.QUEUED)


def test_invalid_transition_raises_and_valid_logs_event(db):
    job = Job(company="A", title="B", source="t", external_id="1", fingerprint="a|b|")
    db.add(job)
    db.flush()
    app = Application(job_id=job.id, status=S.ELIGIBLE.value)
    db.add(app)
    db.flush()
    app.job = job
    with pytest.raises(ServiceError):
        transition(db, app, S.APPLIED)
    transition(db, app, S.QUEUED)
    assert app.status == "QUEUED" and job.status == "QUEUED" and app.events[-1].event == "QUEUED"
