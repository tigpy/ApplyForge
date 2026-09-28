"""Test env is set BEFORE importing the app: temp DB/resume dir, mock AI, mock notifications."""
import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="applyforge-test-")
os.environ.update(
    DATABASE_URL=f"sqlite:///{_tmp}/test.db", RESUME_DIR=f"{_tmp}/resumes", AI_PROVIDER="mock",
    APPLICATION_CONNECTOR="mock", NOTIFICATION_MODE="mock",
)

import pymupdf  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.services.notification_service import MockNotificationService  # noqa: E402

CYBER_TEXT = ("Cybersecurity resume. Skills: Python, Linux, SIEM, Splunk, incident response, networking, "
              "TCP/IP, Wireshark, log analysis, vulnerability assessment. Monitored security alerts in a SOC lab.")
BACKEND_TEXT = "Backend developer resume. Skills: Python, FastAPI, SQL, REST APIs, Git, Docker. Built API services."


def make_pdf(text: str) -> bytes:
    doc = pymupdf.open()
    doc.new_page().insert_textbox(pymupdf.Rect(50, 50, 550, 780), text, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    MockNotificationService.sent.clear()
    yield


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def upload(client, filename: str, text: str):
    return client.post("/api/resumes/upload", files={"file": (filename, make_pdf(text), "application/pdf")})


@pytest.fixture
def seeded(client):
    """Two resumes, a filled profile and discovered mock jobs. Returns jobs keyed by external id (via title)."""
    assert upload(client, "cybersecurity.pdf", CYBER_TEXT).status_code == 201
    assert upload(client, "backend.pdf", BACKEND_TEXT).status_code == 201
    client.put("/api/profile", json={"name": "Test Candidate", "email": "test@example.com", "phone": "+1 555 0100"})
    jobs = client.post("/api/jobs/discover", json={}).json()["jobs"]
    return {j["title"]: j for j in jobs}
