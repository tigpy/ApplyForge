import { useState } from "react";
import { ErrorNote } from "../components/Layout";
import { JobList } from "../components/JobList";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";

export default function Jobs() {
  const { data, error, reload } = useAsync(api.listJobs);
  const [note, setNote] = useState<string | null>(null);

  const [busy, setBusy] = useState(false);

  async function discover() {
    setBusy(true);
    setNote(null);
    try {
      const r = await api.discoverJobs();
      setNote(`${r.discovered} new job(s) discovered`);
      reload();
    } catch (e) {
      setNote((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function runAutomation() {
    setBusy(true);
    setNote(null);
    try {
      const res = await api.runAutomation();
      setNote(`Job search complete: ${res.discovered} discovered, ${res.matched} matched, ${res.applied} applied!`);
      reload();
    } catch (e) {
      setNote((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-bold">Discovered Jobs</h1>
        <div className="flex gap-2">
          <button
            disabled={busy}
            onClick={runAutomation}
            className="rounded bg-blue-700 px-3 py-1 text-sm font-medium text-white hover:bg-blue-800 disabled:opacity-50"
          >
            {busy ? "Running..." : "Run Job Search"}
          </button>
          <button
            disabled={busy}
            onClick={discover}
            className="rounded border border-slate-300 bg-white px-3 py-1 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            Discover jobs
          </button>
        </div>
      </div>
      {note && <p className="text-sm text-slate-700 font-medium">{note}</p>}
      <ErrorNote message={error} />
      <JobList jobs={data ?? []} />
    </>
  );
}
