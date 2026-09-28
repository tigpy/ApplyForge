import { useState } from "react";
import { ApplicationsTable } from "../components/ApplicationsTable";
import { ErrorNote } from "../components/Layout";
import { StatCard } from "../components/StatCard";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";
import type { AutomationRunResult } from "../types";

export default function Dashboard() {
  const jobs = useAsync(api.listJobs);
  const apps = useAsync(api.listApplications);
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<AutomationRunResult | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  const j = jobs.data ?? [];
  const a = apps.data ?? [];
  const count = (s: string) => a.filter((x) => x.status === s).length;

  const todayStr = new Date().toISOString().slice(0, 10);
  const todayApps = a.filter((x) => (x.submitted_at || x.created_at || "").slice(0, 10) === todayStr).length;

  async function handleRunJobSearch() {
    setRunning(true);
    setRunError(null);
    setRunResult(null);
    try {
      const res = await api.runAutomation();
      setRunResult(res);
      jobs.reload();
      apps.reload();
    } catch (e) {
      setRunError((e as Error).message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold">Dashboard</h1>
          <p className="text-xs text-slate-500">Automated job discovery, multi-resume matching, and applications</p>
        </div>
        <button
          disabled={running}
          onClick={handleRunJobSearch}
          className="rounded bg-blue-700 px-4 py-2 font-medium text-white hover:bg-blue-800 disabled:opacity-50 transition shadow-sm text-sm"
        >
          {running ? "Running Job Search..." : "Run Job Search"}
        </button>
      </div>

      <ErrorNote message={runError ?? jobs.error ?? apps.error} />

      {runResult && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-900">
          <div className="font-semibold">Automation Run Completed:</div>
          <div className="flex flex-wrap gap-4 pt-1 text-xs">
            <span>Discovered: <b>{runResult.discovered}</b></span>
            <span>Matched: <b>{runResult.matched}</b></span>
            <span>Eligible: <b>{runResult.eligible}</b></span>
            <span className="text-green-700 font-semibold">Applied: {runResult.applied}</span>
            {runResult.requires_manual_action > 0 && (
              <span className="text-purple-700 font-semibold">Manual Action: {runResult.requires_manual_action}</span>
            )}
            {runResult.blocked > 0 && <span className="text-orange-700">Blocked: {runResult.blocked}</span>}
            {runResult.failed > 0 && <span className="text-red-700">Failed: {runResult.failed}</span>}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 md:grid-cols-6">
        <StatCard label="Jobs discovered" value={j.length} />
        <StatCard label="Jobs matched" value={j.filter((x) => x.match_score !== null).length} />
        <StatCard label="Applications today" value={todayApps} />
        <StatCard label="Applications submitted" value={count("APPLIED")} />
        <StatCard label="Applications failed" value={count("FAILED")} />
        <StatCard label="Applications blocked" value={count("BLOCKED") + count("REQUIRES_MANUAL_ACTION")} />
      </div>

      <h2 className="pt-2 font-semibold">Recent applications</h2>
      <ApplicationsTable applications={a.slice(0, 5)} />
    </>
  );
}
