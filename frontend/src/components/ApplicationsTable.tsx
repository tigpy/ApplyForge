import React from "react";
import { Link } from "react-router-dom";
import type { Application } from "../types";
import { formatDate } from "./format";
import { StatusBadge } from "./StatusBadge";

export function ApplicationsTable({ applications }: { applications: Application[] }) {
  if (applications.length === 0) {
    return (
      <div className="glass-panel p-6 text-center rounded-xl border border-white/5">
        <p className="font-mono text-xs text-gray-500 uppercase tracking-widest">
          NO APPLICATIONS RECORDED // PIPELINE STANDBY
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-xl border border-white/5 overflow-hidden">
      <div className="overflow-x-auto">
        <table data-testid="applications-table" className="w-full text-left text-xs">
          <thead className="border-b border-white/5 bg-white/[0.02] text-gray-400 font-mono text-[10px] uppercase tracking-wider">
            <tr>
              <th className="py-3 px-4">Company</th>
              <th className="py-3 px-4">Role</th>
              <th className="py-3 px-4">Match</th>
              <th className="py-3 px-4">Resume</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {applications.map((a) => (
              <tr
                key={a.id}
                className="hover:bg-white/[0.02] transition-colors group"
              >
                <td className="py-3 px-4 font-semibold text-white">
                  <Link
                    className="text-white hover:text-[#FFB400] transition-colors flex items-center gap-1.5"
                    to={`/applications/${a.id}`}
                  >
                    <span>{a.company}</span>
                    <span className="opacity-0 group-hover:opacity-100 transition-opacity text-[#FF8A00] text-[10px]">
                      →
                    </span>
                  </Link>
                </td>
                <td className="py-3 px-4 text-gray-300 font-medium">
                  {a.role}
                </td>
                <td className="py-3 px-4 font-mono font-bold text-[#FFB400]">
                  {a.match_score !== null && a.match_score !== undefined ? `${a.match_score}%` : "-%"}
                </td>
                <td className="py-3 px-4 font-mono text-[11px] text-gray-400">
                  {a.resume_name ?? "-"}
                </td>
                <td className="py-3 px-4">
                  <StatusBadge status={a.status} />
                </td>
                <td className="py-3 px-4 text-right font-mono text-[11px] text-gray-500">
                  {formatDate(a.submitted_at ?? a.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
