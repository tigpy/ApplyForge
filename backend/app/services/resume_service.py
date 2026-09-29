"""Resume parsing, storage and repository. Original PDFs are stored unmodified."""
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.errors import ServiceError
from app.models import Application, Resume
from app.security import sanitize_filename


class ResumeParser(ABC):
    @abstractmethod
    def extract_text(self, path: Path) -> str: ...


class PyMuPDFResumeParser(ResumeParser):
    def extract_text(self, path: Path) -> str:
        import pymupdf

        with pymupdf.open(path) as doc:
            return "\n".join(page.get_text() for page in doc).strip()


class ResumeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> list[Resume]:
        return self.db.query(Resume).order_by(Resume.id).all()

    def get(self, resume_id: int) -> Resume | None:
        return self.db.get(Resume, resume_id)

    def add(self, resume: Resume) -> Resume:
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def delete(self, resume: Resume) -> None:
        self.db.delete(resume)
        self.db.commit()


def validate_pdf_upload(filename: str, data: bytes) -> None:
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if not filename.lower().endswith(".pdf"):
        raise ServiceError(415, "Only .pdf files are accepted")
    if len(data) > max_bytes:
        raise ServiceError(413, f"File exceeds {settings.max_upload_mb} MB limit")
    if not data.startswith(b"%PDF-"):
        raise ServiceError(415, "File content is not a PDF")


class ResumeService:
    def __init__(self, db: Session, parser: ResumeParser | None = None):
        self.repo = ResumeRepository(db)
        self.db = db
        self.parser = parser or PyMuPDFResumeParser()

    def save_upload(self, filename: str, data: bytes, display_name: str = "", tags: str = "", target_role: str = "") -> Resume:
        validate_pdf_upload(filename, data)
        safe = sanitize_filename(filename)
        settings.resume_path.mkdir(parents=True, exist_ok=True)
        stored = settings.resume_path / f"{uuid.uuid4().hex[:8]}_{safe}"
        stored.write_bytes(data)
        try:
            text = self.parser.extract_text(stored)
        except Exception as exc:  # noqa: BLE001 - corrupt PDF
            stored.unlink(missing_ok=True)
            raise ServiceError(422, "Could not read PDF") from exc
        if not text:
            stored.unlink(missing_ok=True)
            raise ServiceError(422, "PDF has no extractable text (scanned PDFs are not supported)")

        existing = self.db.query(Resume).filter((Resume.extracted_text == text) | ((Resume.filename == safe) & (Resume.extracted_text == text))).first()
        if existing:
            stored.unlink(missing_ok=True)
            raise ServiceError(409, f"A resume with identical content already exists ('{existing.display_name or existing.filename}')")

        return self.repo.add(Resume(
            filename=safe, display_name=display_name.strip() or safe, path=str(stored), extracted_text=text,
            tags=[t.strip() for t in tags.split(",") if t.strip()], target_role=target_role.strip() or None,
            parsed_data={},
        ))

    def delete(self, resume_id: int) -> None:
        resume = self.repo.get(resume_id)
        if resume is None:
            raise ServiceError(404, "Resume not found")
        if self.db.query(Application).filter(Application.resume_id == resume_id).first():
            raise ServiceError(409, "Resume is referenced by an application and cannot be deleted")
        Path(resume.path).unlink(missing_ok=True)
        self.repo.delete(resume)
