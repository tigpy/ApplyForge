import re
import uuid
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup

from packages.connectors.base import JobConnector
from packages.domain.enums import EmploymentType, WorkMode
from packages.shared.security import safe_fetch_url

def clean_text(text: str) -> str:
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def compute_duplicate_fingerprint(company: str, title: str, location: Optional[str]) -> str:
    norm_co = re.sub(r'[^a-z0-9]', '', (company or "").lower())
    norm_ti = re.sub(r'[^a-z0-9]', '', (title or "").lower())
    norm_loc = re.sub(r'[^a-z0-9]', '', (location or "").lower())
    return f"{norm_co}::{norm_ti}::{norm_loc}"

class ManualImportConnector(JobConnector):
    name: str = "manual"

    def health_check(self) -> bool:
        return True

    def search(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        return []

    def get_job(self, external_id: str) -> Optional[Dict[str, Any]]:
        return None

    def fetch_from_url(self, url: str) -> Dict[str, Any]:
        html = safe_fetch_url(url)
        soup = BeautifulSoup(html, "html.parser")
        for element in soup(["script", "style", "noscript", "nav", "footer", "header"]):
            element.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else "Imported Job"
        raw_text = soup.get_text(separator="\n")
        cleaned = clean_text(raw_text)

        return {
            "title": title,
            "url": url,
            "description_raw": cleaned,
            "company": "Extracted Company",
            "location": "Unknown"
        }

    def normalize(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        title = clean_text(raw_job.get("title", "Untitled Job"))
        company = clean_text(raw_job.get("company", "Unknown Company"))
        location = clean_text(raw_job.get("location", "Remote"))
        desc_raw = raw_job.get("description_raw", "")
        desc_norm = clean_text(desc_raw)

        desc_lower = desc_norm.lower()
        if "remote" in desc_lower or "work from home" in desc_lower:
            work_mode = WorkMode.REMOTE
        elif "hybrid" in desc_lower:
            work_mode = WorkMode.HYBRID
        elif "on-site" in desc_lower or "onsite" in desc_lower:
            work_mode = WorkMode.ON_SITE
        else:
            work_mode = raw_job.get("work_mode", WorkMode.REMOTE)

        if "part-time" in desc_lower or "part time" in desc_lower:
            emp_type = EmploymentType.PART_TIME
        elif "contract" in desc_lower or "freelance" in desc_lower:
            emp_type = EmploymentType.CONTRACT
        elif "intern" in desc_lower or "internship" in desc_lower:
            emp_type = EmploymentType.INTERNSHIP
        else:
            emp_type = raw_job.get("employment_type", EmploymentType.FULL_TIME)

        ext_id = raw_job.get("external_id")
        if not ext_id:
            ext_id = str(uuid.uuid4())

        fingerprint = compute_duplicate_fingerprint(company, title, location)

        return {
            "external_id": ext_id,
            "url": raw_job.get("url"),
            "title": title,
            "company": company,
            "location": location,
            "work_mode": work_mode,
            "employment_type": emp_type,
            "description_raw": desc_raw,
            "description_normalized": desc_norm,
            "duplicate_fingerprint": fingerprint
        }
