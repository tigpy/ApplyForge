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
    <>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold">{app.role} · {app.company}</h1>
          <p className="text-sm text-slate-600">
            Resume: {app.resume_name ?? "-"} · Match: {app.match_score ?? "-"}% ·{" "}
            <Link className="text-blue-700 hover:underline" to={`/jobs/${app.job_id}`}>job</Link>
          </p>
        </div>
        <StatusBadge status={app.status} testId="application-status" />
      </div>
      {app.failure_reason && <p className="rounded bg-orange-50 p-2 text-sm text-orange-800">Reason: {app.failure_reason}</p>}
      {app.confirmation_text && <p className="rounded bg-green-50 p-2 text-sm text-green-800">{app.confirmation_text}</p>}
      <h2 className="font-semibold">Events</h2>
      <ul data-testid="event-list" className="divide-y rounded-lg border bg-white text-sm">
        {app.events.map((e) => (
          <li key={e.id} className="p-2">
            <span className="font-mono font-semibold">{e.event}</span>{" "}
            <span className="text-slate-500">{formatDate(e.created_at)}</span>
            {e.details && <pre className="whitespace-pre-wrap text-xs text-slate-600">{e.details}</pre>}
          </li>
        ))}
      </ul>
    </>
  );
}
