"""
Pytest Fixtures and In-Memory Test DB Setup
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from packages.domain.database import Base, get_db
from packages.documents.seed_data import seed_database
from apps.api.main import app
from fastapi.testclient import TestClient

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    
    # Also seed a test job
    from packages.domain.models import Job, JobSource, JobRequirement
    from packages.domain.enums import RequirementType
    src = db.query(JobSource).filter_by(name="mock").first()
    job = Job(
        source_id=src.id,
        external_id="test-job-001",
        title="Junior Security Engineer",
        company="CyberSec Inc",
        location="Remote",
        description_raw="Seeking Junior Security Engineer with Python, Linux, and Security+ certification."
    )
    db.add(job)
    db.flush()
    db.add(JobRequirement(job_id=job.id, requirement_type=RequirementType.SKILL, text="python", normalized_skill="python", mandatory=True))
    db.add(JobRequirement(job_id=job.id, requirement_type=RequirementType.SKILL, text="linux", normalized_skill="linux", mandatory=True))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
