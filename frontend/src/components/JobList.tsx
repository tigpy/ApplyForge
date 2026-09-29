import React from "react";
import { Link } from "react-router-dom";
import type { Job } from "../types";
import { StatusBadge } from "./StatusBadge";

export function JobList({ jobs }: { jobs: Job[] }) {
  if (jobs.length === 0) {
    return (
      <div className="glass-panel p-8 text-center rounded-xl border border-white/5">
        <p className="font-mono text-xs text-gray-500 uppercase tracking-widest">
          NO OPPORTUNITIES INDEXED // RUN DISCOVERY MATRIX
        </p>
      </div>
    );
  }

  return (
    <ul data-testid="job-list" className="space-y-3">
      {jobs.map((j) => (
        <li
          key={j.id}
          className="glass-panel p-4 md:p-5 rounded-xl border border-white/5 hover:border-[#FF8A00]/30 transition-all duration-200 flex flex-col md:flex-row md:items-center justify-between gap-4 group relative overflow-hidden"
        >
          {/* Active left indicator */}
          <span className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-[#FF5A00] to-[#FFB400] opacity-0 group-hover:opacity-100 transition-opacity" />

          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <Link
                className="font-sans font-bold text-base text-white hover:text-[#FFB400] transition-colors"
                to={`/jobs/${j.id}`}
              >
                {j.title} · {j.company}
              </Link>
              <StatusBadge status={j.status} />
            </div>

            <div className="font-mono text-xs text-gray-400 flex flex-wrap items-center gap-2">
              <span>{j.location}</span>
              <span>•</span>
              <span className="uppercase text-[#FFB400]/80">{j.remote_type}</span>
              <span>•</span>
              <span className="text-gray-500 uppercase">SRC: {j.source}</span>
            </div>

            {j.selected_resume_name && (
              <div className="mt-1.5 flex items-center gap-1.5 font-mono text-xs text-[#FFB400] bg-[#FF8A00]/10 px-2 py-0.5 rounded border border-[#FF8A00]/20 w-fit">
                <span className="w-1 h-1 rounded-full bg-[#FFB400]" />
                <span>Best Resume: {j.selected_resume_name}</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4 shrink-0 border-t md:border-t-0 pt-3 md:pt-0 border-white/5 justify-between md:justify-end">
            <div className="text-right">
              <span className="block font-mono text-[9px] text-gray-500 uppercase tracking-widest">
                VECTOR MATCH
              </span>
              <span className="font-mono text-xl md:text-2xl font-black text-[#FFB400]">
                {j.match_score === null ? "not matched" : `${j.match_score}%`}
              </span>
            </div>
            <Link
              to={`/jobs/${j.id}`}
              className="p-2 rounded-lg bg-white/[0.03] hover:bg-[#FF8A00]/20 border border-white/10 hover:border-[#FFB400]/40 text-gray-300 hover:text-white transition-all text-xs font-mono"
            >
              DETAILS →
            </Link>
          </div>
        </li>
      ))}
    </ul>
  );
}
