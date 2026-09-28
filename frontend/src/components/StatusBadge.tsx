import type { Status } from "../types";

const COLORS: Record<Status, string> = {
  APPLIED: "bg-green-100 text-green-800",
  FAILED: "bg-red-100 text-red-800",
  BLOCKED: "bg-orange-100 text-orange-800",
  APPLYING: "bg-blue-100 text-blue-800",
  QUEUED: "bg-blue-100 text-blue-800",
  ELIGIBLE: "bg-emerald-100 text-emerald-800",
  MATCHED: "bg-sky-100 text-sky-800",
  DISCOVERED: "bg-slate-100 text-slate-700",
  SKIPPED: "bg-slate-200 text-slate-600",
  DUPLICATE: "bg-yellow-100 text-yellow-800",
};

export function StatusBadge({ status, testId }: { status: Status; testId?: string }) {
  return (
    <span data-testid={testId} className={`rounded px-2 py-0.5 text-xs font-semibold ${COLORS[status]}`}>
      {status}
    </span>
  );
}
