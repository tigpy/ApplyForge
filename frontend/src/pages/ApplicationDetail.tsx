import React from "react";
import { Link, useParams } from "react-router-dom";
import { formatDate } from "../components/format";
import { ErrorNote } from "../components/Layout";
import { StatusBadge } from "../components/StatusBadge";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";

export default function ApplicationDetail() {
  const id = Number(useParams().id);
  const { data: app, error } = useAsync(() => api.getApplication(id), [id]);
  if (!app) return <ErrorNote message={error} />;

  return (
    <div className="space-y-6">
      {/* Header Card */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 font-mono text-[10px] text-gray-400 uppercase tracking-widest">
            <span className="px-2 py-0.5 rounded font-bold bg-[#FF8A00]/20 text-[#FFB400] border border-[#FF8A00]/30">
              APP//DETAIL #{app.id}
            </span>
            <span>//</span>
            <span>DISPATCH CONSOLE</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight font-sans">
            {app.role} · {app.company}
          </h1>
          <p className="text-xs font-mono text-gray-300 mt-2">
            Resume: <span className="text-white font-semibold">{app.resume_name ?? "-"}</span> · Match:{" "}
            <span className="text-[#FFB400] font-bold">{app.match_score ?? "-"}%</span> ·{" "}
            <Link className="text-[#FFB400] underline hover:text-white transition-colors" to={`/jobs/${app.job_id}`}>
              job
            </Link>
          </p>
        </div>
        <StatusBadge status={app.status} testId="application-status" />
      </div>

      {app.failure_reason && (
        <div className="glass-panel p-4 rounded-xl border border-red-500/30 bg-red-950/20 text-xs font-mono text-red-300">
          <b>Reason: </b>{app.failure_reason}
        </div>
      )}

      {app.confirmation_text && (
        <div className="glass-panel p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/20 text-xs font-mono text-emerald-300">
          {app.confirmation_text}
        </div>
      )}

      {/* Events Timeline */}
      <div className="space-y-3">
        <h2 className="font-mono text-xs font-bold text-gray-300 uppercase tracking-wider px-1">
          Events
        </h2>
        <ul data-testid="event-list" className="space-y-2.5">
          {app.events.map((e) => (
            <li
              key={e.id}
              className="glass-panel p-3.5 rounded-xl border border-white/5 space-y-1.5"
            >
              <div className="flex items-center justify-between font-mono text-xs">
                <span className="font-bold text-[#FFB400]">{e.event}</span>
                <span className="text-gray-500 text-[10px]">{formatDate(e.created_at)}</span>
              </div>
              {e.details && (
                <pre className="whitespace-pre-wrap text-[11px] font-mono text-gray-400 bg-black/40 p-2.5 rounded-lg border border-white/5">
                  {e.details}
                </pre>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
