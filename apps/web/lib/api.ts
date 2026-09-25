/**
 * Typed API Client for ApplyForge FastAPI backend
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1';

export interface Candidate {
  id: number;
  name: string;
  email: string;
  phone?: string;
  location?: string;
  work_authorization: string;
  skills: Array<{ id: number; name: string; category: string; proficiency: string }>;
  educations: Array<{ id: number; institution: string; degree: string; field: string; grade?: string }>;
  projects: Array<{ id: number; name: string; description: string; technologies: string[] }>;
  experiences: Array<{ id: number; organization: string; title: string; description: string }>;
  certifications: Array<{ id: number; name: string; issuer: string }>;
  resumes: Array<{ id: number; name: string; job_family: string; version: number }>;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  location?: string;
  work_mode: string;
  employment_type: string;
  description_raw: string;
  discovered_at: string;
  requirements?: Array<{ id: number; requirement_type: string; text: string }>;
}

export interface Application {
  id: number;
  candidate_id: number;
  job_id: number;
  resume_id?: number;
  status: string;
  approved_at?: string;
  submitted_at?: string;
  notes?: string;
  job?: Job;
  questions?: Array<{
    id: number;
    question: string;
    answer?: string;
    final_answer?: string;
    answer_source: string;
    requires_review: boolean;
  }>;
}

export const api = {
  async getCandidate(): Promise<Candidate | null> {
    const res = await fetch(`${API_BASE}/candidate/profile`);
    return res.ok ? res.json() : null;
  },

  async getJobs(): Promise<Job[]> {
    const res = await fetch(`${API_BASE}/jobs`);
    return res.ok ? res.json() : [];
  },

  async getQueue(): Promise<Application[]> {
    const res = await fetch(`${API_BASE}/applications/queue`);
    return res.ok ? res.json() : [];
  },

  async getApplications(): Promise<Application[]> {
    const res = await fetch(`${API_BASE}/applications`);
    return res.ok ? res.json() : [];
  },

  async getResumes(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/resumes/variants`);
    return res.ok ? res.json() : [];
  },

  async getSources(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/connectors/sources`);
    return res.ok ? res.json() : [];
  },

  async getAuditLogs(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/audit/logs`);
    return res.ok ? res.json() : [];
  },

  async prepareApplication(jobId: number): Promise<Application> {
    const res = await fetch(`${API_BASE}/applications/prepare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId }),
    });
    if (!res.ok) throw new Error('Failed to prepare application');
    return res.json();
  },

  async approveApplication(appId: number): Promise<Application> {
    const res = await fetch(`${API_BASE}/applications/${appId}/approve`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to approve application');
    return res.json();
  },

  async rejectApplication(appId: number, notes?: string): Promise<Application> {
    const res = await fetch(`${API_BASE}/applications/${appId}/reject?notes=${encodeURIComponent(notes || '')}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to reject application');
    return res.json();
  },

  async submitApplication(appId: number): Promise<Application> {
    const res = await fetch(`${API_BASE}/applications/${appId}/submit`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to submit application');
    }
    return res.json();
  },

  async triggerDiscovery(platform = 'mock'): Promise<any> {
    const res = await fetch(`${API_BASE}/connectors/discover?platform=${platform}`, { method: 'POST' });
    return res.json();
  },
};
