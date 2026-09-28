import type { Application, Job, Resume } from "../types";

export const resume: Resume = {
  id: 1, filename: "cybersecurity.pdf", display_name: "cybersecurity.pdf", tags: ["security"],
  target_role: "SOC Analyst", extracted_chars: 420, created_at: "2026-09-28T08:00:00",
};
export const job: Job = {
  id: 1, company: "Example Corp", title: "Junior Security Analyst", location: "Toronto", remote_type: "hybrid",
  url: "", application_url: "", source: "mock", requirements: ["Python"], discovered_at: "2026-09-28T08:00:00",
  status: "ELIGIBLE", match_score: 91, selected_resume_id: 1, application_id: 1,
};
export const application: Application = {
  id: 1, job_id: 1, resume_id: 1, status: "APPLIED", match_score: 91, application_url: "mock://apply/x",
  submitted_at: "2026-09-28T09:00:00", failure_reason: null, confirmation_text: "ok",
  created_at: "2026-09-28T08:30:00", updated_at: "2026-09-28T09:00:00",
  company: "Example Corp", role: "Junior Security Analyst", resume_name: "cybersecurity.pdf",
};
