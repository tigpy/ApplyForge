import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ErrorNote } from "../components/Layout";
import { StatusBadge } from "../components/StatusBadge";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";

const APPLYABLE = ["ELIGIBLE", "FAILED", "BLOCKED", "REQUIRES_MANUAL_ACTION"];

export default function JobDetail() {
  const id = Number(useParams().id);
  const navigate = useNavigate();
  const { data: job, error, reload } = useAsync(() => api.getJob(id), [id]);
  const [actionError, setActionError] = useState<string | null>(null);

  const run = (fn: () => Promise<unknown>) => async () => {
    setActionError(null);
    try { await fn(); } catch (e) { setActionError((e as Error).message); }
  };

  if (!job) return <ErrorNote message={error} />;
  const m = job.match;
  const canApply = m?.application_id && m.application_status && APPLYABLE.includes(m.application_status);

  return (
    <>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold">{job.title}</h1>
          <p className="text-slate-600">{job.company} · {job.location} · {job.remote_type}</p>
        </div>
        <StatusBadge status={job.status} />
      </div>
      <p className="whitespace-pre-line rounded-lg border bg-white p-3 text-sm">{job.description}</p>
      <div>
        <h2 className="font-semibold">Requirements</h2>
        <ul className="list-disc pl-5 text-sm">{job.requirements.map((r) => <li key={r}>{r}</li>)}</ul>
      </div>
      <ErrorNote message={actionError} />
      <div className="flex gap-2 items-center">
        {job.status === "APPLIED" || m?.application_status === "APPLIED" ? (
          <div className="rounded bg-green-50 border border-green-200 px-3 py-1.5 text-sm text-green-900 font-medium">
            ✓ Applied · Resume used: <span className="font-semibold">{m?.selected_resume_name || job.selected_resume_name || "Resume"}</span>
          </div>
        ) : (
          <>
            <button className="rounded bg-blue-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-800" onClick={run(async () => { await api.matchJob(id); reload(); })}>
              Match
            </button>
            <button className="rounded bg-green-700 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-800"
              onClick={run(async () => { const a = await api.applyJob(job.id); navigate(`/applications/${a.id}`); })}>
              Apply
            </button>
          </>
        )}
      </div>
      {m && (
        <section className="space-y-3 rounded-lg border bg-white p-4 text-sm">
          <div className="flex flex-wrap gap-6 border-b pb-3">
            <div>Match Score: <b data-testid="match-score" className="text-base text-blue-700">{m.score}%</b></div>
            <div>Best Resume: <b data-testid="match-resume">{m.selected_resume_name}</b></div>
            <div>Recommendation: <b data-testid="match-recommendation">{m.recommendation}</b></div>
          </div>
          {m.explanation && <div className="text-xs text-slate-600 bg-slate-50 p-2 rounded">{m.explanation}</div>}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <b className="text-emerald-700">Matched Skills:</b>
              <ul className="mt-1 list-disc pl-5 text-xs text-slate-700">
                {(m.matched_skills && m.matched_skills.length > 0) ? m.matched_skills.map((s) => <li key={s}>{s}</li>) :
                 m.strengths.map((s) => <li key={s}>{s}</li>)}
              </ul>
            </div>
            <div>
              <b className="text-rose-700">Missing Requirements:</b>
              <ul className="mt-1 list-disc pl-5 text-xs text-slate-700">
                {(m.missing_skills || m.missing_requirements).length > 0 ?
                  (m.missing_skills || m.missing_requirements).map((s) => <li key={s}>{s}</li>) :
                  <li>None (all required skills satisfied)</li>
                }
              </ul>
            </div>
          </div>
          <div><b>All evaluated resumes:</b> {m.resume_scores.map((s) => `${s.resume_name} (${s.score}%)`).join(", ")}</div>
        </section>
      )}

    </>
  );
}
