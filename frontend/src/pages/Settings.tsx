import { useEffect, useState } from "react";
import { ErrorNote } from "../components/Layout";
import { api } from "../services/api";
import type { Profile } from "../types";

const EMPTY: Profile = {
  name: "", email: "", phone: "", location: "", linkedin: "", github: "", portfolio: "",
  education: [], skills: [], experience: [], facts: {},
  target_roles: [], preferred_locations: [], remote_preference: "all",
  min_experience: 0, salary_preference: "", excluded_roles: [],
  excluded_companies: [], preferred_job_sources: ["mock"],
};
const TEXT_FIELDS = ["name", "email", "phone", "location", "linkedin", "github", "portfolio"] as const;

export default function Settings() {
  const [profile, setProfile] = useState<Profile>(EMPTY);
  const [targetRolesText, setTargetRolesText] = useState("");
  const [prefLocationsText, setPrefLocationsText] = useState("");
  const [exRolesText, setExRolesText] = useState("");
  const [exCompaniesText, setExCompaniesText] = useState("");
  const [jobSourcesText, setJobSourcesText] = useState("");
  const [factsText, setFactsText] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getProfile().then((p) => {
      setProfile(p);
      setTargetRolesText((p.target_roles || []).join("\n"));
      setPrefLocationsText((p.preferred_locations || []).join("\n"));
      setExRolesText((p.excluded_roles || []).join("\n"));
      setExCompaniesText((p.excluded_companies || []).join("\n"));
      setJobSourcesText((p.preferred_job_sources || ["mock"]).join(", "));
      setFactsText(Object.entries(p.facts || {}).map(([k, v]) => `${k}=${v}`).join("\n"));
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
      const updated: Profile = {
        ...profile,
        target_roles: targetRolesText.split("\n").map((s) => s.trim()).filter(Boolean),
        preferred_locations: prefLocationsText.split("\n").map((s) => s.trim()).filter(Boolean),
        excluded_roles: exRolesText.split("\n").map((s) => s.trim()).filter(Boolean),
        excluded_companies: exCompaniesText.split("\n").map((s) => s.trim()).filter(Boolean),
        preferred_job_sources: jobSourcesText.split(",").map((s) => s.trim()).filter(Boolean),
        facts: parseFacts(),
      };
      const saved = await api.saveProfile(updated);
      setProfile(saved);
      setMessage("Preferences and profile saved successfully");
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function testEmail() {
    setError(null);
    try {
      setMessage((await api.testEmail()).detail);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const input = "w-full rounded border p-1 text-sm bg-white";
  return (
    <>
      <h1 className="text-xl font-bold">Preferences & Settings</h1>
      <p className="text-sm text-slate-600">
        Configure your target roles, locations, exclusions, and verified facts. Only verified information is ever used to apply.
      </p>
      <ErrorNote message={error} />
      {message && <p className="text-sm text-green-700 font-medium">{message}</p>}

      {/* Job Search Preferences */}
      <div className="rounded-lg border bg-white p-4 space-y-4">
        <h2 className="font-semibold text-base text-slate-900 border-b pb-2">Job Search Preferences</h2>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="text-sm font-medium text-slate-700">
            Target Roles (one per line)
            <textarea
              className={input}
              rows={4}
              placeholder="SOC Analyst&#10;Cybersecurity Analyst&#10;Security Engineer&#10;Java Backend Developer"
              value={targetRolesText}
              onChange={(e) => setTargetRolesText(e.target.value)}
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Preferred Locations (one per line)
            <textarea
              className={input}
              rows={4}
              placeholder="Mumbai&#10;Remote&#10;India"
              value={prefLocationsText}
              onChange={(e) => setPrefLocationsText(e.target.value)}
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Workplace Preference
            <select
              className={input}
              value={profile.remote_preference}
              onChange={(e) => setProfile({ ...profile, remote_preference: e.target.value })}
            >
              <option value="all">Any (Remote, Hybrid, or On-site)</option>
              <option value="remote">Remote only</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-site</option>
            </select>
          </label>
          <label className="text-sm font-medium text-slate-700">
            Minimum Experience (Years)
            <input
              type="number"
              min={0}
              className={input}
              value={profile.min_experience}
              onChange={(e) => setProfile({ ...profile, min_experience: Number(e.target.value) || 0 })}
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Salary Expectation (optional)
            <input
              className={input}
              placeholder="e.g. ₹12,000,000 / $100k"
              value={profile.salary_preference}
              onChange={(e) => setProfile({ ...profile, salary_preference: e.target.value })}
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Job Sources (comma separated)
            <input
              className={input}
              placeholder="mock, public_feed"
              value={jobSourcesText}
              onChange={(e) => setJobSourcesText(e.target.value)}
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Excluded Roles (one per line)
            <textarea
              className={input}
              rows={2}
              placeholder="Sales, Marketing, HR"
              value={exRolesText}
              onChange={(e) => setExRolesText(e.target.value)}
            />
          </label>
          <label className="text-sm font-medium text-slate-700">
            Excluded Companies (one per line)
            <textarea
              className={input}
              rows={2}
              placeholder="Suspicious Corp, Scam Ltd"
              value={exCompaniesText}
              onChange={(e) => setExCompaniesText(e.target.value)}
            />
          </label>
        </div>
      </div>

      {/* Candidate Profile Info */}
      <div className="rounded-lg border bg-white p-4 space-y-4">
        <h2 className="font-semibold text-base text-slate-900 border-b pb-2">Candidate Profile</h2>
        <div className="grid gap-3 md:grid-cols-2">
          {TEXT_FIELDS.map((f) => (
            <label key={f} className="text-sm font-medium text-slate-700 capitalize">
              {f}
              <input
                className={input}
                value={profile[f]}
                onChange={(e) => setProfile({ ...profile, [f]: e.target.value })}
              />
            </label>
          ))}
          <label className="text-sm font-medium text-slate-700 md:col-span-2">
            Verified Answers (key=value per line, e.g. work_authorization=Yes)
            <textarea
              className={input}
              rows={3}
              value={factsText}
              onChange={(e) => setFactsText(e.target.value)}
            />
          </label>
        </div>
      </div>

      <div className="flex gap-2">
        <button onClick={save} className="rounded bg-blue-700 px-4 py-1.5 text-sm font-medium text-white hover:bg-blue-800">
          Save preferences
        </button>
        <button onClick={testEmail} className="rounded border px-4 py-1.5 text-sm hover:bg-slate-50">
          Send test notification
        </button>
      </div>
    </>
  );
}

