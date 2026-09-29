import React, { useState } from "react";
import type { Resume } from "../types";
import { formatDate } from "./format";

export function ResumeList({
  resumes,
  onDelete,
}: {
  resumes: Resume[];
  onDelete?: (id: number) => void;
}) {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  if (resumes.length === 0) {
    return (
      <div className="glass-panel p-8 text-center rounded-xl border border-white/5">
        <p className="font-mono text-xs text-gray-500 uppercase tracking-widest">
          NO RESUME PROFILES INGESTED // UPLOAD PDF VECTOR
        </p>
      </div>
    );
  }

  return (
    <ul data-testid="resume-list" className="space-y-3">
      {resumes.map((r) => {
        const isExpanded = expandedId === r.id;
        return (
          <li
            key={r.id}
            className="glass-panel p-4 md:p-5 rounded-xl border border-white/5 hover:border-[#FF8A00]/30 transition-all duration-200 group"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#FFB400] shadow-[0_0_6px_#FFB400]" />
                  <span className="font-sans font-bold text-base text-white group-hover:text-[#FFB400] transition-colors">
                    {r.filename}
                  </span>
                </div>
                <div className="font-mono text-xs text-gray-400 flex flex-wrap items-center gap-2">
                  {r.display_name !== r.filename && (
                    <span className="text-gray-300 font-medium">{r.display_name} · </span>
                  )}
                  {r.target_role && (
                    <span className="text-[#FFB400] font-semibold bg-[#FF8A00]/10 px-1.5 py-0.5 rounded border border-[#FF8A00]/20">
                      {r.target_role}
                    </span>
                  )}
                  {r.tags.length > 0 && (
                    <span className="text-gray-500">[{r.tags.join(", ")}]</span>
                  )}
                  <span className="text-gray-500">
                    {r.extracted_chars} chars · {formatDate(r.created_at)}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3 shrink-0 pt-2 sm:pt-0 border-t sm:border-t-0 border-white/5">
                <button
                  type="button"
                  className="font-mono text-xs px-3 py-1.5 rounded-lg bg-white/[0.03] hover:bg-white/[0.08] text-gray-300 hover:text-white border border-white/10 transition-colors"
                  onClick={() => setExpandedId(isExpanded ? null : r.id)}
                >
                  {isExpanded ? "Hide preview" : "Preview text"}
                </button>
                {onDelete && (
                  <button
                    className="font-mono text-xs px-3 py-1.5 rounded-lg bg-red-950/30 hover:bg-red-900/50 text-red-400 hover:text-red-300 border border-red-500/20 transition-colors"
                    onClick={() => onDelete(r.id)}
                  >
                    Delete
                  </button>
                )}
              </div>
            </div>

            {isExpanded && (
              <div className="mt-4 rounded-xl bg-black/60 p-4 text-xs text-gray-300 font-mono whitespace-pre-wrap max-h-60 overflow-y-auto border border-white/10 shadow-inner">
                {r.extracted_text || "No text extracted."}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
