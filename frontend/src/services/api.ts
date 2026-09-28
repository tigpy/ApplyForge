import type { Application, ApplicationDetail, AutomationRunResult, Job, JobDetail, MatchResult, Profile, Resume } from "../types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, init);
  if (!res.ok) {
    let message = res.statusText;
    try {
      const body = await res.json();
      message = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch { /* keep statusText */ }
    throw new Error(message);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

const json = (method: string, body?: unknown): RequestInit => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: body === undefined ? undefined : JSON.stringify(body),
});

export const api = {
  listResumes: () => request<Resume[]>("/resumes"),
  uploadResume: (file: File, opts: { displayName?: string; tags?: string; targetRole?: string } = {}) => {
    const form = new FormData();
    form.append("file", file);
    form.append("display_name", opts.displayName ?? "");
    form.append("tags", opts.tags ?? "");
    form.append("target_role", opts.targetRole ?? "");
    return request<Resume>("/resumes/upload", { method: "POST", body: form });
  },
  deleteResume: (id: number) => request<void>(`/resumes/${id}`, { method: "DELETE" }),

  listJobs: () => request<Job[]>("/jobs"),
  getJob: (id: number) => request<JobDetail>(`/jobs/${id}`),
  discoverJobs: () => request<{ discovered: number; jobs: Job[] }>("/jobs/discover", json("POST", {})),
  matchJob: (id: number) => request<MatchResult>(`/jobs/${id}/match`, json("POST")),

  listApplications: () => request<Application[]>("/applications"),
  getApplication: (id: number) => request<ApplicationDetail>(`/applications/${id}`),
  applyTo: (id: number) => request<ApplicationDetail>(`/applications/${id}/apply`, json("POST")),

  getProfile: () => request<Profile>("/profile"),
  saveProfile: (p: Profile) => request<Profile>("/profile", json("PUT", p)),
  testEmail: () => request<{ sent: boolean; mode: string; detail: string }>("/settings/test-email", json("POST")),

  runAutomation: (opts?: { connector?: string; query?: string; auto_apply?: boolean }) =>
    request<AutomationRunResult>("/automation/run", json("POST", opts ?? {})),
};
