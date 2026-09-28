import { useEffect, useState } from "react";
import { ErrorNote } from "../components/Layout";
import { api } from "../services/api";
import type { Profile } from "../types";

const EMPTY: Profile = {
  name: "", email: "", phone: "", location: "", linkedin: "", github: "", portfolio: "",
  education: [], skills: [], experience: [], facts: {},
};
const TEXT_FIELDS = ["name", "email", "phone", "location", "linkedin", "github", "portfolio"] as const;
const LIST_FIELDS = ["education", "skills", "experience"] as const;

export default function Settings() {
  const [profile, setProfile] = useState<Profile>(EMPTY);
  const [factsText, setFactsText] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getProfile().then((p) => {
      setProfile(p);
      setFactsText(Object.entries(p.facts).map(([k, v]) => `${k}=${v}`).join("\n"));
    }).catch((e: Error) => setError(e.message));
  }, []);

  const parseFacts = () =>
    Object.fromEntries(factsText.split("\n").filter((l) => l.includes("=")).map((l) => {
      const i = l.indexOf("=");
      return [l.slice(0, i).trim(), l.slice(i + 1).trim()];
    }));

  async function save() {
    setError(null);
    try {
      setProfile(await api.saveProfile({ ...profile, facts: parseFacts() }));
      setMessage("Profile saved");
    } catch (e) { setError((e as Error).message); }
  }

  async function testEmail() {
    setError(null);
    try { setMessage((await api.testEmail()).detail); } catch (e) { setError((e as Error).message); }
  }

  const input = "w-full rounded border p-1 text-sm";
  return (
    <>
      <h1 className="text-xl font-bold">Settings</h1>
      <p className="text-sm text-slate-600">
        Only information stored here and in your resumes is ever used to fill applications. Anything else is left for manual handling.
      </p>
      <ErrorNote message={error} />
      {message && <p className="text-sm text-green-700">{message}</p>}
      <section className="grid gap-2 rounded-lg border bg-white p-3 md:grid-cols-2">
        {TEXT_FIELDS.map((f) => (
          <label key={f} className="text-sm capitalize">{f}
            <input className={input} value={profile[f]} onChange={(e) => setProfile({ ...profile, [f]: e.target.value })} />
          </label>
        ))}
        {LIST_FIELDS.map((f) => (
          <label key={f} className="text-sm capitalize">{f} (one per line)
            <textarea className={input} rows={3} value={profile[f].join("\n")}
              onChange={(e) => setProfile({ ...profile, [f]: e.target.value.split("\n").filter(Boolean) })} />
          </label>
        ))}
        <label className="text-sm md:col-span-2">Verified answers (key=value per line, e.g. work_authorization=Yes)
          <textarea className={input} rows={3} value={factsText} onChange={(e) => setFactsText(e.target.value)} />
        </label>
      </section>
      <div className="flex gap-2">
        <button onClick={save} className="rounded bg-blue-700 px-3 py-1 text-sm text-white">Save profile</button>
        <button onClick={testEmail} className="rounded border px-3 py-1 text-sm">Send test notification</button>
      </div>
    </>
  );
}
