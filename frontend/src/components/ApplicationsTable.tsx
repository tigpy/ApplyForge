import { Link } from "react-router-dom";
import type { Application } from "../types";
import { formatDate } from "./format";
import { StatusBadge } from "./StatusBadge";

export function ApplicationsTable({ applications }: { applications: Application[] }) {
  if (applications.length === 0) return <p className="text-slate-500">No applications yet.</p>;
  return (
    <table data-testid="applications-table" className="w-full bg-white text-left text-sm">
      <thead className="border-b text-slate-500">
        <tr><th className="p-2">Company</th><th>Role</th><th>Match</th><th>Resume</th><th>Status</th><th>Date</th></tr>
      </thead>
      <tbody>
        {applications.map((a) => (
          <tr key={a.id} className="border-b">
            <td className="p-2"><Link className="text-blue-700 hover:underline" to={`/applications/${a.id}`}>{a.company}</Link></td>
            <td>{a.role}</td>
            <td>{a.match_score ?? "-"}%</td>
            <td>{a.resume_name ?? "-"}</td>
            <td><StatusBadge status={a.status} /></td>
            <td>{formatDate(a.submitted_at ?? a.created_at)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
