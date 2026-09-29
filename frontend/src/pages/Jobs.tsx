import React, { useState } from "react";
import { ErrorNote } from "../components/Layout";
import { JobList } from "../components/JobList";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";

export default function Jobs() {
  const { data, error, reload } = useAsync(api.listJobs);
  const [note, setNote] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function discover() {
    setBusy(true);
    setNote(null);
    try {
      const r = await api.discoverJobs();
      setNote(`${r.discovered} new job(s) discovered`);
      reload();
    } catch (e) {
      setNote((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function runAutomation() {
    setBusy(true);
    setNote(null);
    try {
      const res = await api.runAutomation();
      setNote(
        `Job search complete: ${res.discovered} discovered, ${res.matched} matched, ${res.applied} applied!`
      );
      reload();
    } catch (e) {
      setNote((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded font-mono text-[9px] font-bold bg-[#FF8A00]/20 text-[#FFB400] border border-[#FF8A00]/30 tracking-wider">
              JOB//03 MATRIX
            </span>
            <span className="text-gray-600 font-mono text-xs">//</span>
            <span className="font-mono text-xs text-gray-400 tracking-widest uppercase">
              OPPORTUNITY DISCOVERY & VECTOR RANKING
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white font-sans">
            Discovered Jobs
          </h1>
          <p className="text-xs text-gray-400 font-mono mt-1">
            DISCOVERY ENGINE: READY // CONTINUOUS FEED HARVESTING // ATS PREPARATION
          </p>
        </div>

        {/* Discovery Action Controls */}
        <div className="flex items-center gap-3">
          <button
            disabled={busy}
            onClick={runAutomation}
            className="px-4 py-2 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-[#FF5A00] to-[#FFB400] text-black hover:shadow-[0_0_16px_rgba(255,180,0,0.35)] disabled:opacity-50 transition-all"
          >
            {busy ? "Running..." : "Run Job Search"}
          </button>
          <button
            disabled={busy}
            onClick={discover}
            className="px-4 py-2 rounded-xl font-mono text-xs font-semibold uppercase tracking-wider bg-white/[0.03] hover:bg-white/[0.08] text-gray-200 border border-white/10 hover:border-[#FFB400]/40 disabled:opacity-50 transition-all"
          >
            Discover jobs
          </button>
        </div>
      </div>

      {note && (
        <div className="glass-panel p-3.5 rounded-xl border border-[#FFB400]/30 bg-[#FF8A00]/10 text-xs font-mono text-[#FFB400] flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#FFB400] animate-pulse shrink-0" />
          <span>{note}</span>
        </div>
      )}

      <ErrorNote message={error} />

      {/* Discovered Job Feed */}
      <div>
        <div className="flex items-center justify-between mb-3 px-1">
          <div className="flex items-center gap-2 font-mono text-xs font-semibold text-gray-300 uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FF8A00]" />
            <span>OPPORTUNITY FEED ({data?.length ?? 0})</span>
          </div>
          <span className="font-mono text-[10px] text-gray-500 uppercase">
            SORTED BY RECENCY
          </span>
        </div>
        <JobList jobs={data ?? []} />
      </div>
    </div>
  );
}
