import React, { useEffect, useState } from "react";
import { ErrorNote } from "../components/Layout";
import { api } from "../services/api";
import type { Profile } from "../types";

const EMPTY: Profile = {
  name: "",
  email: "",
  phone: "",
  location: "",
  linkedin: "",
  github: "",
  portfolio: "",
  education: [],
  skills: [],
  experience: [],
  facts: {},
  target_roles: [],
  preferred_locations: [],
  remote_preference: "all",
  min_experience: 0,
  salary_preference: "",
  excluded_roles: [],
  excluded_companies: [],
  preferred_job_sources: ["mock"],
};
const TEXT_FIELDS = [
  "name",
  "email",
  "phone",
  "location",
  "linkedin",
  "github",
  "portfolio",
] as const;

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
    api
      .getProfile()
      .then((p) => {
        setProfile(p);
        setTargetRolesText((p.target_roles || []).join("\n"));
        setPrefLocationsText((p.preferred_locations || []).join("\n"));
        setExRolesText((p.excluded_roles || []).join("\n"));
        setExCompaniesText((p.excluded_companies || []).join("\n"));
        setJobSourcesText((p.preferred_job_sources || ["mock"]).join(", "));
        setFactsText(
          Object.entries(p.facts || {})
            .map(([k, v]) => `${k}=${v}`)
            .join("\n")
        );
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  const parseFacts = () =>
    Object.fromEntries(
      factsText
        .split("\n")
        .filter((l) => l.includes("="))
        .map((l) => {
          const i = l.indexOf("=");
          return [l.slice(0, i).trim(), l.slice(i + 1).trim()];
        })
    );

  async function save() {
    setError(null);
    try {
      const updated: Profile = {
        ...profile,
        target_roles: targetRolesText
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        preferred_locations: prefLocationsText
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        excluded_roles: exRolesText
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        excluded_companies: exCompaniesText
          .split("\n")
          .map((s) => s.trim())
          .filter(Boolean),
        preferred_job_sources: jobSourcesText
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
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

  const inputClass =
    "w-full rounded-lg border border-white/10 bg-black/60 p-2.5 text-xs font-mono text-white placeholder-gray-500 focus:outline-none focus:border-[#FFB400] focus:ring-1 focus:ring-[#FFB400] transition-colors";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-3 pb-4 border-b border-white/5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded font-mono text-[9px] font-bold bg-[#FF8A00]/20 text-[#FFB400] border border-[#FF8A00]/30 tracking-wider">
              CFG//05 AGENT
            </span>
            <span className="text-gray-600 font-mono text-xs">//</span>
            <span className="font-mono text-xs text-gray-400 tracking-widest uppercase">
              AGENT DIRECTIVES & CANDIDATE DATA
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white font-sans">
            Preferences & Settings
          </h1>
          <p className="text-xs text-gray-400 font-mono mt-1">
            Configure your target roles, locations, exclusions, and verified facts. Only verified information is ever used to apply.
          </p>
        </div>
      </div>

      <ErrorNote message={error} />
      {message && (
        <div className="glass-panel p-3.5 rounded-xl border border-emerald-500/30 bg-emerald-950/20 text-xs font-mono text-emerald-300 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <span>{message}</span>
        </div>
      )}

      {/* Job Search Preferences */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h2 className="font-mono text-xs font-bold text-gray-200 uppercase tracking-wider border-b border-white/5 pb-2">
          Job Search Preferences
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          <label className="text-xs font-mono text-gray-300">
            Target Roles (one per line)
            <textarea
              className={`mt-1.5 ${inputClass}`}
              rows={4}
              placeholder={"SOC Analyst\nCybersecurity Analyst\nSecurity Engineer\nJava Backend Developer"}
              value={targetRolesText}
              onChange={(e) => setTargetRolesText(e.target.value)}
            />
          </label>
          <label className="text-xs font-mono text-gray-300">
            Preferred Locations (one per line)
            <textarea
              className={`mt-1.5 ${inputClass}`}
              rows={4}
              placeholder={"Mumbai\nRemote\nIndia"}
              value={prefLocationsText}
              onChange={(e) => setPrefLocationsText(e.target.value)}
            />
          </label>
          <label className="text-xs font-mono text-gray-300">
            Workplace Preference
            <select
              className={`mt-1.5 ${inputClass}`}
              value={profile.remote_preference}
              onChange={(e) => setProfile({ ...profile, remote_preference: e.target.value })}
            >
              <option value="all">Any (Remote, Hybrid, or On-site)</option>
              <option value="remote">Remote only</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">On-site</option>
            </select>
          </label>
          <label className="text-xs font-mono text-gray-300">
            Minimum Experience (Years)
            <input
              type="number"
              min={0}
              className={`mt-1.5 ${inputClass}`}
              value={profile.min_experience}
              onChange={(e) => setProfile({ ...profile, min_experience: Number(e.target.value) || 0 })}
            />
          </label>
          <label className="text-xs font-mono text-gray-300">
            Salary Expectation (optional)
            <input
              className={`mt-1.5 ${inputClass}`}
              placeholder="e.g. ₹12,000,000 / $100k"
              value={profile.salary_preference}
              onChange={(e) => setProfile({ ...profile, salary_preference: e.target.value })}
            />
          </label>
          <label className="text-xs font-mono text-gray-300">
            Job Sources (comma separated)
            <input
              className={`mt-1.5 ${inputClass}`}
              placeholder="mock, public_feed"
              value={jobSourcesText}
              onChange={(e) => setJobSourcesText(e.target.value)}
            />
          </label>
          <label className="text-xs font-mono text-gray-300">
            Excluded Roles (one per line)
            <textarea
              className={`mt-1.5 ${inputClass}`}
              rows={2}
              placeholder="Sales, Marketing, HR"
              value={exRolesText}
              onChange={(e) => setExRolesText(e.target.value)}
            />
          </label>
          <label className="text-xs font-mono text-gray-300">
            Excluded Companies (one per line)
            <textarea
              className={`mt-1.5 ${inputClass}`}
              rows={2}
              placeholder="Suspicious Corp, Scam Ltd"
              value={exCompaniesText}
              onChange={(e) => setExCompaniesText(e.target.value)}
            />
          </label>
        </div>
      </div>

      {/* Candidate Profile Info */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h2 className="font-mono text-xs font-bold text-gray-200 uppercase tracking-wider border-b border-white/5 pb-2">
          Candidate Profile
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          {TEXT_FIELDS.map((f) => (
            <label key={f} className="text-xs font-mono text-gray-300 capitalize">
              {f}
              <input
                className={`mt-1.5 ${inputClass}`}
                value={profile[f]}
                onChange={(e) => setProfile({ ...profile, [f]: e.target.value })}
              />
            </label>
          ))}
          <label className="text-xs font-mono text-gray-300 md:col-span-2">
            Verified Answers (key=value per line, e.g. work_authorization=Yes)
            <textarea
              className={`mt-1.5 ${inputClass}`}
              rows={3}
              value={factsText}
              onChange={(e) => setFactsText(e.target.value)}
            />
          </label>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={save}
          className="px-5 py-2.5 rounded-xl font-mono text-xs font-bold uppercase tracking-wider bg-gradient-to-r from-[#FF5A00] to-[#FFB400] text-black hover:shadow-[0_0_16px_rgba(255,180,0,0.35)] transition-all"
        >
          Save preferences
        </button>
        <button
          onClick={testEmail}
          className="px-5 py-2.5 rounded-xl font-mono text-xs font-semibold uppercase tracking-wider bg-white/[0.03] hover:bg-white/[0.08] text-gray-200 border border-white/10 hover:border-white/20 transition-all"
        >
          Send test notification
        </button>
      </div>
    </div>
  );
}
