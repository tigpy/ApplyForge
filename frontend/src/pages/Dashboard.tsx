import { ApplicationsTable } from "../components/ApplicationsTable";
import { ErrorNote } from "../components/Layout";
import { StatCard } from "../components/StatCard";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";

export default function Dashboard() {
  const jobs = useAsync(api.listJobs);
  const apps = useAsync(api.listApplications);
  const j = jobs.data ?? [];
  const a = apps.data ?? [];
  const count = (s: string) => a.filter((x) => x.status === s).length;

  return (
    <>
      <h1 className="text-xl font-bold">Dashboard</h1>
      <ErrorNote message={jobs.error ?? apps.error} />
      <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
        <StatCard label="Jobs discovered" value={j.length} />
        <StatCard label="Jobs matched" value={j.filter((x) => x.match_score !== null).length} />
        <StatCard label="Applications submitted" value={count("APPLIED")} />
        <StatCard label="Applications failed" value={count("FAILED")} />
        <StatCard label="Applications blocked" value={count("BLOCKED")} />
      </div>
      <h2 className="pt-2 font-semibold">Recent applications</h2>
      <ApplicationsTable applications={a.slice(0, 5)} />
    </>
  );
}
