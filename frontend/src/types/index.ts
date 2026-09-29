export type Status =
  | "DISCOVERED" | "MATCHED" | "ELIGIBLE" | "QUEUED" | "APPLYING"
  | "APPLIED" | "FAILED" | "SKIPPED" | "DUPLICATE" | "BLOCKED"
  | "REQUIRES_MANUAL_ACTION";

export interface Resume {
  id: number; filename: string; display_name: string; tags: string[];
  target_role: string | null; extracted_chars: number; extracted_text: string; created_at: string;
}
export interface ResumeScore { resume_id: number; resume_name: string; score: number }
export interface MatchResult {
  id: number; job_id: number; selected_resume_id: number | null; selected_resume_name: string | null;
  score: number; strengths: string[]; missing_requirements: string[]; reasons: string[];
  recommendation: "APPLY" | "SKIP"; resume_scores: ResumeScore[];
  application_id: number | null; application_status: Status | null; created_at: string;
  resume_id?: number | null; matched_skills?: string[]; missing_skills?: string[];
  matched_certifications?: string[]; role_match?: boolean; experience_match?: boolean; explanation?: string;
}
export interface Job {
  id: number; company: string; title: string; location: string; remote_type: string; url: string;
  application_url: string; source: string; requirements: string[]; discovered_at: string; status: Status;
  match_score: number | null; selected_resume_id: number | null; selected_resume_name?: string | null; application_id: number | null;
}
export interface JobDetail extends Job { description: string; match: MatchResult | null }
export interface ApplicationEvent { id: number; event: string; details: string; created_at: string }
export interface ApplicationResult {
  application_id: number; job_id: number; company: string; role: string;
  selected_resume_id: number | null; resume_name: string | null; match_score: number | null;
  status: Status; submitted_at: string | null; confirmation_text: string | null;
  failure_reason: string | null; application_url: string; created_at: string;
}

export interface Application {
  id: number; job_id: number; resume_id: number | null; status: Status; match_score: number | null;
  application_url: string; submitted_at: string | null; failure_reason: string | null;
  confirmation_text: string | null; created_at: string; updated_at: string;
  company: string; role: string; resume_name: string | null;
}
export interface ApplicationDetail extends Application { events: ApplicationEvent[] }
export interface Profile {
  name: string; email: string; phone: string; location: string; linkedin: string; github: string;
  portfolio: string; education: string[]; skills: string[]; experience: string[]; facts: Record<string, string>;
  target_roles: string[]; preferred_locations: string[]; remote_preference: string;
  min_experience: number; salary_preference: string; excluded_roles: string[];
  excluded_companies: string[]; preferred_job_sources: string[];
}
export interface AutomationRunResult {
  discovered: number; matched: number; eligible: number; applied: number;
  requires_manual_action: number; blocked: number; failed: number;
  skipped: number; duplicate: number; remaining?: number; details: Array<{
    job_id: number; company: string; role: string; resume: string | null;
    match_score: number; status: string; message: string;
  }>;
}
