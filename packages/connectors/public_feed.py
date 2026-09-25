import re
import uuid
from typing import Any, Dict, List, Optional
import requests
from packages.connectors.base import JobConnector
from packages.domain.enums import EmploymentType, WorkMode
from packages.connectors.manual import clean_text, compute_duplicate_fingerprint

class PublicFeedConnector(JobConnector):
    name: str = "public_feed"
    FEED_URL: str = "https://jobicy.com/api/v2/remote-jobs?count=10"

    def health_check(self) -> bool:
        try:
            r = requests.get(self.FEED_URL, timeout=5)
            return r.status_code == 200
        except Exception:
            return False

    def search(self, query: str = "", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            headers = {"User-Agent": "JobApplicationAutomation/1.0"}
            res = requests.get(self.FEED_URL, headers=headers, timeout=10)
            if res.status_code != 200:
                return []
            data = res.json()
            jobs = data.get("jobs", [])
            results = []
            for item in jobs:
                if query:
                    q_lower = query.lower()
                    title = item.get("jobTitle", "").lower()
                    desc = item.get("jobDescription", "").lower()
                    if q_lower not in title and q_lower not in desc:
                        continue
                results.append(self.normalize(item))
            return results
        except Exception:
            return []

    def get_job(self, external_id: str) -> Optional[Dict[str, Any]]:
        jobs = self.search("")
        for j in jobs:
            if j["external_id"] == external_id:
                return j
        return None

    def normalize(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        ext_id = str(raw_job.get("id") or raw_job.get("external_id") or uuid.uuid4())
        title = clean_text(raw_job.get("jobTitle") or raw_job.get("title", "Untitled Job"))
        company = clean_text(raw_job.get("companyName") or raw_job.get("company", "Unknown Company"))
        location = clean_text(raw_job.get("jobGeo") or raw_job.get("location", "Remote"))
        url = raw_job.get("url") or raw_job.get("jobUrl")

        # Strip HTML tags from description if present
        raw_desc = raw_job.get("jobDescription") or raw_job.get("description_raw", "")
        clean_desc = re.sub(r'<[^>]+>', ' ', raw_desc)
        clean_desc = clean_text(clean_desc)

        fingerprint = compute_duplicate_fingerprint(company, title, location)

        return {
            "external_id": ext_id,
            "url": url,
            "title": title,
            "company": company,
            "location": location,
            "work_mode": WorkMode.REMOTE,
            "employment_type": EmploymentType.FULL_TIME,
            "description_raw": clean_desc,
            "description_normalized": clean_desc,
            "duplicate_fingerprint": fingerprint
        }
