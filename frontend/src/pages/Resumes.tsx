import { useRef, useState } from "react";
import { ErrorNote } from "../components/Layout";
import { ResumeList } from "../components/ResumeList";
import { useAsync } from "../hooks/useAsync";
import { api } from "../services/api";

export default function Resumes() {
  const { data, error, reload } = useAsync(api.listResumes);
  const fileRef = useRef<HTMLInputElement>(null);
  const [displayName, setDisplayName] = useState("");
  const [tags, setTags] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [busy, setBusy] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  async function upload() {
    const file = fileRef.current?.files?.[0];
    if (!file) return setUploadError("Choose a PDF first");
    setBusy(true);
    setUploadError(null);
    try {
      await api.uploadResume(file, { displayName, tags, targetRole });
      if (fileRef.current) fileRef.current.value = "";
      setDisplayName(""); setTags(""); setTargetRole("");
      reload();
    } catch (e) {
      setUploadError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const input = "rounded border p-1 text-sm";
  return (
    <>
      <h1 className="text-xl font-bold">Resume Manager</h1>
      <div className="flex flex-wrap items-end gap-2 rounded-lg border bg-white p-3">
        <input data-testid="resume-file" ref={fileRef} type="file" accept="application/pdf,.pdf" className="text-sm" />
        <input className={input} placeholder="Display name" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
        <input className={input} placeholder="Tags (comma separated)" value={tags} onChange={(e) => setTags(e.target.value)} />
        <input className={input} placeholder="Target role" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} />
        <button disabled={busy} onClick={upload} className="rounded bg-blue-700 px-3 py-1 text-sm text-white disabled:opacity-50">Upload</button>
      </div>
      <ErrorNote message={uploadError ?? error} />
      <ResumeList resumes={data ?? []} onDelete={(id) => api.deleteResume(id).then(reload).catch((e: Error) => setUploadError(e.message))} />
    </>
  );
}
