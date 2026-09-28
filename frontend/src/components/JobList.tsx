import { Link } from "react-router-dom";
import type { Job } from "../types";
import { StatusBadge } from "./StatusBadge";

export function JobList({ jobs }: { jobs: Job[] }) {
  if (jobs.length === 0) return <p className="text-slate-500">No jobs discovered yet.</p>;
  return (
    <ul data-testid="job-list" className="divide-y rounded-lg border bg-white">
      {jobs.map((j) => (
        <li key={j.id} className="flex items-center justify-between p-3">
          <div>
            <Link className="font-medium text-blue-700 hover:underline" to={`/jobs/${j.id}`}>
              {j.title} · {j.company}
            </Link>
            <div className="text-xs text-slate-500">{j.location} · {j.remote_type} · {j.source}</div>
            {j.selected_resume_name && (
              <div className="mt-0.5 text-xs text-indigo-700 font-medium">Best Resume: {j.selected_resume_name}</div>
            )}
          </div>
          <div className="flex items-center gap-3 text-sm">
            <span className="font-semibold">{j.match_score === null ? "not matched" : `${j.match_score}%`}</span>
            <StatusBadge status={j.status} />
          </div>

        </li>
      ))}
    </ul>
  );
}
