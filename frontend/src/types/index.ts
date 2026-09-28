export type Status =
  | "DISCOVERED" | "MATCHED" | "ELIGIBLE" | "QUEUED" | "APPLYING"
  | "APPLIED" | "FAILED" | "SKIPPED" | "DUPLICATE" | "BLOCKED";

export interface Resume {
  id: number; filename: string; display_name: string; tags: string[];
  target_role: string | null; extracted_chars: number; created_at: string;
}
export interface ResumeScore { resume_id: number; resume_name: string; score: number }
export interface MatchResult {
  id: number; job_id: number; selected_resume_id: number | null; selected_resume_name: string | null;
  score: number; strengths: string[]; missing_requirements: string[]; reasons: string[];
  recommendation: "APPLY" | "SKIP"; resume_scores: ResumeScore[];
  application_id: number | null; application_status: Status | null; created_at: string;
}
export interface Job {
  id: number; company: string; title: string; location: string; remote_type: string; url: string;
  application_url: string; source: string; requirements: string[]; discovered_at: string; status: Status;
  match_score: number | null; selected_resume_id: number | null; application_id: number | null;
}
export interface JobDetail extends Job { description: string; match: MatchResult | null }
export interface ApplicationEvent { id: number; event: string; details: string; created_at: string }
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
}
