import React, { useState } from "react";
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
    try {
      await fn();
    } catch (e) {
      setActionError((e as Error).message);
    }
  };

  if (!job) return <ErrorNote message={error} />;
  const m = job.match;

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 font-mono text-[10px] text-gray-400 uppercase tracking-widest">
            <span className="px-2 py-0.5 rounded font-bold bg-[#FF8A00]/20 text-[#FFB400] border border-[#FF8A00]/30">
              JOB//ANALYSIS #{job.id}
            </span>
            <span>//</span>
            <span>INTEL DOSSIER</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight font-sans">
            {job.title}
          </h1>
          <p className="text-xs font-mono text-gray-300 mt-1">
            {job.company} · {job.location} · <span className="text-[#FFB400] uppercase">{job.remote_type}</span>
          </p>
        </div>
        <StatusBadge status={job.status} />
      </div>

      {/* Action Controls & Application State Banner */}
      <div className="flex items-center gap-3">
        {job.status === "APPLIED" || m?.application_status === "APPLIED" ? (
          <div className="w-full glass-panel p-4 rounded-xl border border-emerald-500/30 bg-emerald-950/20 text-xs font-mono text-emerald-300 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34D399]" />
            <span>
              ✓ Applied · Resume used:{" "}
              <b className="text-white font-bold">{m?.selected_resume_name || job.selected_resume_name || "Resume"}</b>
            </span>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <button
              className="px-5 py-2 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-white/[0.04] hover:bg-white/[0.08] text-white border border-white/15 hover:border-[#FFB400]/40 transition-all"
              onClick={run(async () => {
                await api.matchJob(id);
                reload();
              })}
            >
              Match
            </button>
            <button
              className="px-5 py-2 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-[#FF5A00] to-[#FFB400] text-black hover:shadow-[0_0_16px_rgba(255,180,0,0.35)] transition-all"
              onClick={run(async () => {
                const a = await api.applyJob(job.id);
                navigate(`/applications/${a.id}`);
              })}
            >
              Apply
            </button>
          </div>
        )}
      </div>

      <ErrorNote message={actionError} />

      {/* MATCH ANALYSIS REPORT */}
      {m && (
        <section className="glass-panel p-6 rounded-2xl border border-[#FF8A00]/25 space-y-5">
          <div className="flex items-center justify-between border-b border-white/5 pb-3">
            <div className="flex items-center gap-2 font-mono text-xs font-bold text-white uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-[#FFB400] shadow-[0_0_8px_#FFB400]" />
              <span>COGNITIVE MATCH ANALYSIS</span>
            </div>
            <span className="font-mono text-[10px] text-[#FFB400]">
              ALGORITHM // HYBRID VECTOR
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
            <div className="p-3 rounded-xl bg-black/40 border border-white/5">
              <span className="text-gray-400 block text-[10px] uppercase">Match Score</span>
              <b data-testid="match-score" className="text-2xl font-black text-[#FFB400] block mt-1">
                {m.score}%
              </b>
            </div>
            <div className="p-3 rounded-xl bg-black/40 border border-white/5">
              <span className="text-gray-400 block text-[10px] uppercase">Best Resume</span>
              <b data-testid="match-resume" className="text-sm font-bold text-white block mt-1.5 truncate">
                {m.selected_resume_name}
              </b>
            </div>
            <div className="p-3 rounded-xl bg-black/40 border border-white/5">
              <span className="text-gray-400 block text-[10px] uppercase">Recommendation</span>
              <b
                data-testid="match-recommendation"
                className={`text-sm font-bold block mt-1.5 ${
                  m.recommendation === "APPLY" ? "text-emerald-400" : "text-amber-400"
                }`}
              >
                {m.recommendation}
              </b>
            </div>
          </div>

          {m.explanation && (
            <div className="text-xs font-mono text-gray-300 bg-black/50 p-3 rounded-xl border border-white/5 leading-relaxed">
              <span className="text-[#FFB400] font-semibold">AI RATIONALE // </span>
              {m.explanation}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-black/30 border border-emerald-500/20">
              <b className="text-xs font-mono text-emerald-400 uppercase tracking-wider block mb-2">
                Matched Skills:
              </b>
              <ul className="space-y-1 text-xs font-mono text-gray-300">
                {m.matched_skills && m.matched_skills.length > 0
                  ? m.matched_skills.map((s) => (
                      <li key={s} className="flex items-center gap-1.5">
                        <span className="w-1 h-1 rounded-full bg-emerald-400" />
                        <span>{s}</span>
                      </li>
                    ))
                  : m.strengths.map((s) => (
                      <li key={s} className="flex items-center gap-1.5">
                        <span className="w-1 h-1 rounded-full bg-emerald-400" />
                        <span>{s}</span>
                      </li>
                    ))}
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-black/30 border border-rose-500/20">
              <b className="text-xs font-mono text-rose-400 uppercase tracking-wider block mb-2">
                Missing Requirements:
              </b>
              <ul className="space-y-1 text-xs font-mono text-gray-300">
                {(m.missing_skills || m.missing_requirements).length > 0 ? (
                  (m.missing_skills || m.missing_requirements).map((s) => (
                    <li key={s} className="flex items-center gap-1.5">
                      <span className="w-1 h-1 rounded-full bg-rose-400" />
                      <span>{s}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-gray-500">None (all required skills satisfied)</li>
                )}
              </ul>
            </div>
          </div>

          <div className="text-xs font-mono text-gray-400 pt-2 border-t border-white/5">
            <b>All evaluated resumes:</b>{" "}
            {m.resume_scores.map((s) => `${s.resume_name} (${s.score}%)`).join(", ")}
          </div>
        </section>
      )}

      {/* Description & Structured Requirements */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <div>
          <h2 className="font-mono text-xs font-bold text-gray-300 uppercase tracking-wider mb-2">
            Requirements
          </h2>
          <ul className="space-y-1.5 text-xs font-mono text-gray-300">
            {job.requirements.map((r) => (
              <li key={r} className="flex items-start gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[#FFB400] shrink-0 mt-1" />
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="pt-4 border-t border-white/5">
          <h2 className="font-mono text-xs font-bold text-gray-300 uppercase tracking-wider mb-2">
            Job Description
          </h2>
          <p className="whitespace-pre-line text-xs font-mono text-gray-400 leading-relaxed bg-black/40 p-4 rounded-xl border border-white/5">
            {job.description}
          </p>
        </div>
      </div>
    </div>
  );
}
