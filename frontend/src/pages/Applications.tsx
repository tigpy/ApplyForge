import React from "react";
import { ApplicationsTable } from "../components/ApplicationsTable";
import { ErrorNote } from "../components/Layout";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";

export default function Applications() {
  const { data, error } = useAsync(api.listApplications);
  const a = data ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-3 pb-4 border-b border-white/5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded font-mono text-[9px] font-bold bg-[#FF8A00]/20 text-[#FFB400] border border-[#FF8A00]/30 tracking-wider">
              APP//04 CONTROL
            </span>
            <span className="text-gray-600 font-mono text-xs">//</span>
            <span className="font-mono text-xs text-gray-400 tracking-widest uppercase">
              APPLICATION EXECUTION LOG
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white font-sans">
            Application History
          </h1>
          <p className="text-xs text-gray-400 font-mono mt-1">
            DISPATCH AUDIT // REAL-TIME STATUS TRACKING // APPLIED EVIDENCE ARCHIVE
          </p>
        </div>
      </div>

      <ErrorNote message={error} />

      {/* Applications Operational Console */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2 font-mono text-xs font-semibold text-gray-300 uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FFB400]" />
            <span>DISPATCHED PIPELINE RECORDS ({a.length})</span>
          </div>
        </div>
        <ApplicationsTable applications={a} />
      </div>
    </div>
  );
}
