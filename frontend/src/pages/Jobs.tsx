import { useState } from "react";
import { ErrorNote } from "../components/Layout";
import { JobList } from "../components/JobList";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";

export default function Jobs() {
  const { data, error, reload } = useAsync(api.listJobs);
  const [note, setNote] = useState<string | null>(null);

  async function discover() {
    try {
      const r = await api.discoverJobs();
      setNote(`${r.discovered} new job(s) discovered`);
      reload();
    } catch (e) {
      setNote((e as Error).message);
    }
  }

  return (
    <>
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Discovered Jobs</h1>
        <button onClick={discover} className="rounded bg-blue-700 px-3 py-1 text-sm text-white">Discover jobs</button>
      </div>
      {note && <p className="text-sm text-slate-600">{note}</p>}
      <ErrorNote message={error} />
      <JobList jobs={data ?? []} />
    </>
  );
}
