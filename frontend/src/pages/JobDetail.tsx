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
      <div className="flex gap-2">
        <button className="rounded bg-blue-700 px-3 py-1 text-sm text-white" onClick={run(async () => { await api.matchJob(id); reload(); })}>
          Run match
        </button>
        {canApply && (
          <button className="rounded bg-green-700 px-3 py-1 text-sm text-white"
            onClick={run(async () => { const a = await api.applyTo(m!.application_id!); navigate(`/applications/${a.id}`); })}>
            Apply now
          </button>
        )}
      </div>
      {m && (
        <section className="space-y-2 rounded-lg border bg-white p-3 text-sm">
          <div className="flex gap-6">
            <div>Score: <b data-testid="match-score">{m.score}</b>%</div>
            <div>Resume: <b data-testid="match-resume">{m.selected_resume_name}</b></div>
            <div>Recommendation: <b data-testid="match-recommendation">{m.recommendation}</b></div>
          </div>
          <div><b>Strengths:</b> {m.strengths.join("; ") || "-"}</div>
          <div><b>Missing:</b> {m.missing_requirements.join(", ") || "none"}</div>
          <div><b>Reasons:</b> {m.reasons.join(" | ")}</div>
          <div><b>All resumes:</b> {m.resume_scores.map((s) => `${s.resume_name} ${s.score}%`).join(", ")}</div>
        </section>
      )}
    </>
  );
}
