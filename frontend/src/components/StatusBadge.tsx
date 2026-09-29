import React from "react";
import type { Status } from "../types";

const COLORS: Record<Status, string> = {
  APPLIED: "bg-emerald-950/40 text-emerald-300 border border-emerald-500/30",
  FAILED: "bg-red-950/40 text-red-300 border border-red-500/30",
  BLOCKED: "bg-orange-950/40 text-orange-300 border border-orange-500/30",
  APPLYING: "bg-[#FF8A00]/15 text-[#FFB400] border border-[#FF8A00]/30 animate-pulse",
  QUEUED: "bg-cyan-950/40 text-cyan-300 border border-cyan-500/30",
  ELIGIBLE: "bg-teal-950/40 text-teal-300 border border-teal-500/30",
  MATCHED: "bg-[#FF8A00]/10 text-[#FFB400] border border-[#FF8A00]/25",
  DISCOVERED: "bg-white/[0.04] text-gray-300 border border-white/10",
  SKIPPED: "bg-white/[0.02] text-gray-500 border border-white/5",
  DUPLICATE: "bg-amber-950/40 text-amber-300 border border-amber-500/30",
  REQUIRES_MANUAL_ACTION: "bg-purple-950/40 text-purple-300 border border-purple-500/30",
};

export function StatusBadge({ status, testId }: { status: Status; testId?: string }) {
  return (
    <span
      data-testid={testId}
      className={`inline-flex items-center gap-1 rounded px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider ${COLORS[status]}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-70" />
      {status}
    </span>
  );
}
