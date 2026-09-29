import React, { useRef, useState } from "react";
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
      setDisplayName("");
      setTags("");
      setTargetRole("");
      reload();
    } catch (e) {
      setUploadError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const inputStyle =
    "rounded-lg border border-white/10 bg-black/60 px-3 py-2 text-xs font-mono text-white placeholder-gray-500 focus:outline-none focus:border-[#FFB400] focus:ring-1 focus:ring-[#FFB400] transition-colors";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-3 pb-4 border-b border-white/5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded font-mono text-[9px] font-bold bg-[#FF8A00]/20 text-[#FFB400] border border-[#FF8A00]/30 tracking-wider">
              RES//02 ASSETS
            </span>
            <span className="text-gray-600 font-mono text-xs">//</span>
            <span className="font-mono text-xs text-gray-400 tracking-widest uppercase">
              VECTOR PROFILE REPOSITORY
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white font-sans">
            Resume Intelligence
          </h1>
          <p className="text-xs text-gray-400 font-mono mt-1">
            Manage the documents the AI uses for candidate matching.
          </p>
        </div>
      </div>

      {/* Upload Drop Zone Panel */}
      <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-4">
        <div className="flex items-center justify-between border-b border-white/5 pb-2.5">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FFB400]" />
            <span className="font-mono text-xs font-semibold text-gray-200 uppercase tracking-wider">
              [ + ADD RESUME ]
            </span>
          </div>
          <span className="font-mono text-[10px] text-gray-500 uppercase">
            SUPPORTED: PDF // MAX 5MB
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="md:col-span-1">
            <label className="block text-[10px] font-mono text-gray-400 uppercase mb-1">
              Select Document
            </label>
            <input
              data-testid="resume-file"
              ref={fileRef}
              type="file"
              accept="application/pdf,.pdf"
              className="w-full text-xs text-gray-300 font-mono file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-mono file:bg-[#FF8A00]/20 file:text-[#FFB400] hover:file:bg-[#FF8A00]/30 cursor-pointer"
            />
          </div>

          <div>
            <label className="block text-[10px] font-mono text-gray-400 uppercase mb-1">
              Display Name (Optional)
            </label>
            <input
              className={`w-full ${inputStyle}`}
              placeholder="e.g. Cybersecurity Lead"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-[10px] font-mono text-gray-400 uppercase mb-1">
              Target Role (Optional)
            </label>
            <input
              className={`w-full ${inputStyle}`}
              placeholder="e.g. Security Analyst"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-[10px] font-mono text-gray-400 uppercase mb-1">
              Tags (Comma separated)
            </label>
            <div className="flex gap-2">
              <input
                className={`flex-1 ${inputStyle}`}
                placeholder="soc, python, siem"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
              />
              <button
                disabled={busy}
                onClick={upload}
                className="px-4 py-2 rounded-lg font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-[#FF5A00] to-[#FFB400] text-black hover:shadow-[0_0_16px_rgba(255,180,0,0.3)] disabled:opacity-50 transition-all shrink-0"
              >
                {busy ? "Ingesting..." : "Upload"}
              </button>
            </div>
          </div>
        </div>
      </div>

      <ErrorNote message={uploadError ?? error} />

      {/* Resume Asset List */}
      <div>
        <div className="flex items-center justify-between mb-3 px-1">
          <div className="flex items-center gap-2 font-mono text-xs font-semibold text-gray-300 uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FF8A00]" />
            <span>ACTIVE RESUME PROFILES ({data?.length ?? 0})</span>
          </div>
        </div>
        <ResumeList
          resumes={data ?? []}
          onDelete={(id) =>
            api
              .deleteResume(id)
              .then(reload)
              .catch((e: Error) => setUploadError(e.message))
          }
        />
      </div>
    </div>
  );
}
