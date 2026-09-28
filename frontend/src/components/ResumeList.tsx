import { useState } from "react";
import type { Resume } from "../types";
import { formatDate } from "./format";

export function ResumeList({ resumes, onDelete }: { resumes: Resume[]; onDelete?: (id: number) => void }) {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  if (resumes.length === 0) return <p className="text-slate-500">No resumes uploaded yet.</p>;
  return (
    <ul data-testid="resume-list" className="divide-y rounded-lg border bg-white">
      {resumes.map((r) => {
        const isExpanded = expandedId === r.id;
        return (
          <li key={r.id} className="p-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium">{r.filename}</div>
                <div className="text-xs text-slate-500">
                  {r.display_name !== r.filename && <>{r.display_name} · </>}
                  {r.target_role && <span className="font-semibold text-slate-700">{r.target_role} · </span>}
                  {r.tags.length > 0 && <>{r.tags.join(", ")} · </>}
                  {r.extracted_chars} chars · {formatDate(r.created_at)}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  className="text-xs text-blue-700 hover:underline"
                  onClick={() => setExpandedId(isExpanded ? null : r.id)}
                >
                  {isExpanded ? "Hide preview" : "Preview text"}
                </button>
                {onDelete && (
                  <button className="text-sm text-red-700 hover:underline" onClick={() => onDelete(r.id)}>
                    Delete
                  </button>
                )}
              </div>
            </div>
            {isExpanded && (
              <div className="mt-2 rounded bg-slate-50 p-2 text-xs text-slate-700 font-mono whitespace-pre-wrap max-h-48 overflow-y-auto border">
                {r.extracted_text || "No text extracted."}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
