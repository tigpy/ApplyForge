import type { Resume } from "../types";
import { formatDate } from "./format";

export function ResumeList({ resumes, onDelete }: { resumes: Resume[]; onDelete?: (id: number) => void }) {
  if (resumes.length === 0) return <p className="text-slate-500">No resumes uploaded yet.</p>;
  return (
    <ul data-testid="resume-list" className="divide-y rounded-lg border bg-white">
      {resumes.map((r) => (
        <li key={r.id} className="flex items-center justify-between p-3">
          <div>
            <div className="font-medium">{r.filename}</div>
            <div className="text-xs text-slate-500">
              {r.display_name !== r.filename && <>{r.display_name} · </>}
              {r.target_role && <>{r.target_role} · </>}
              {r.tags.join(", ")} {r.tags.length > 0 && "· "}
              {r.extracted_chars} chars · {formatDate(r.created_at)}
            </div>
          </div>
          {onDelete && (
            <button className="text-sm text-red-700 hover:underline" onClick={() => onDelete(r.id)}>Delete</button>
          )}
        </li>
      ))}
    </ul>
  );
}
