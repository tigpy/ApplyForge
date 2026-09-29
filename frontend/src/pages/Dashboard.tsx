import React, { useEffect, useState } from "react";
import { AIReactor, type ReactorState } from "../components/ai/AIReactor";
import { AISystemLog, type LogEntry } from "../components/ai/AISystemLog";
import { AISystemStatus } from "../components/ai/AISystemStatus";
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
  const [reactorState, setReactorState] = useState<ReactorState>("IDLE");
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const j = jobs.data ?? [];
  const a = apps.data ?? [];
  const count = (s: string) => a.filter((x) => x.status === s).length;

  const todayStr = new Date().toISOString().slice(0, 10);
  const todayApps = a.filter(
    (x) => (x.submitted_at || x.created_at || "").slice(0, 10) === todayStr
  ).length;

  // Initialize initial system telemetry logs based on real loaded state
  useEffect(() => {
    const now = () =>
      new Date().toLocaleTimeString("en-US", { hour12: false });
    const initialLogs: LogEntry[] = [
      { id: "1", time: now(), message: "APPLYFORGE SYSTEM INITIALIZED // CORE ONLINE", level: "INFO" },
      { id: "2", time: now(), message: "JOB SOURCES CONNECTED // DISCOVERY READY", level: "INFO" },
    ];
    if (j.length > 0) {
      initialLogs.push({
        id: "3",
        time: now(),
        message: `${String(j.length).padStart(2, "0")} OPPORTUNITIES INDEXED IN SYSTEM DATABASE`,
        level: "AI",
      });
    }
    if (a.length > 0) {
      initialLogs.push({
        id: "4",
        time: now(),
        message: `${String(a.length).padStart(2, "0")} APPLICATION CYCLES RECORDED // GUARDRAILS ACTIVE`,
        level: "SUCCESS",
      });
    }
    setLogs(initialLogs);
  }, [j.length, a.length]);

  async function handleRunJobSearch() {
    setRunning(true);
    setRunError(null);
    setRunResult(null);
    setReactorState("SCANNING");

    const now = () =>
      new Date().toLocaleTimeString("en-US", { hour12: false });

    setLogs((prev) => [
      ...prev,
      { id: String(Date.now()), time: now(), message: "AUTONOMOUS JOB DISCOVERY & APPLICATION CYCLE INITIATED", level: "AI" },
    ]);

    try {
      const res = await api.runAutomation();
      setRunResult(res);
      jobs.reload();
      apps.reload();

      setReactorState("COMPLETE");
      setLogs((prev) => [
        ...prev,
        {
          id: String(Date.now() + 1),
          time: now(),
          message: `SCAN COMPLETE: ${res.discovered} DISCOVERED // ${res.matched} MATCHED // ${res.applied} APPLIED`,
          level: "SUCCESS",
        },
      ]);

      // Reset to idle after 5 seconds
      setTimeout(() => {
        setReactorState("IDLE");
      }, 5000);
    } catch (e) {
      const err = (e as Error).message;
      setRunError(err);
      setReactorState("ERROR");
      setLogs((prev) => [
        ...prev,
        { id: String(Date.now() + 2), time: now(), message: `CYCLE HALTED: ${err.toUpperCase()}`, level: "WARN" },
      ]);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* TOP SYSTEM HEADER */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-4 border-b border-white/5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded font-mono text-[9px] font-bold bg-[#FF8A00]/20 text-[#FFB400] border border-[#FF8A00]/30 tracking-wider">
              SYS//01 COMMAND CENTER
            </span>
            <span className="text-gray-600 font-mono text-xs">//</span>
            <span className="font-mono text-xs text-gray-400 tracking-widest uppercase">
              AUTONOMOUS APPLICATION SYSTEM
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white font-sans">
            Dashboard
          </h1>
          <p className="text-xs text-gray-400 font-mono mt-1">
            AI-DRIVEN DISCOVERY / MULTI-RESUME MATCHING / APPLICATION ORCHESTRATION
          </p>
        </div>

        {/* Global Action Button */}
        <div className="flex items-center gap-3">
          <button
            disabled={running}
            onClick={handleRunJobSearch}
            className={`relative group px-5 py-2.5 rounded-xl font-mono text-xs font-bold tracking-wider uppercase transition-all duration-300 flex items-center gap-2.5 overflow-hidden ${
              running
                ? "bg-[#FF8A00]/20 text-[#FFB400] border border-[#FFB400]/40 cursor-wait"
                : "bg-gradient-to-r from-[#FF5A00] to-[#FFB400] text-black hover:shadow-[0_0_24px_rgba(255,180,0,0.4)] active:scale-[0.98]"
            }`}
          >
            <span className="absolute inset-0 w-full h-full bg-white/20 -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
            <span className={`w-2 h-2 rounded-full ${running ? "bg-[#FFB400] animate-ping" : "bg-black"}`} />
            <span>{running ? "Running Job Search..." : "Run Job Search"}</span>
          </button>
        </div>
      </div>

      <ErrorNote message={runError ?? jobs.error ?? apps.error} />

      {/* AUTOMATION RESULT HUD */}
      {runResult && (
        <div className="glass-panel p-4 rounded-xl border border-[#FFB400]/40 bg-[#FF8A00]/5 shadow-[0_0_24px_rgba(255,180,0,0.15)] animate-in fade-in duration-300">
          <div className="flex items-center justify-between border-b border-white/5 pb-2 mb-3">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="font-mono text-xs font-bold text-white uppercase tracking-wider">
                AUTOMATION CYCLE EXECUTED
              </span>
            </div>
            <span className="font-mono text-[10px] text-[#FFB400] uppercase">
              STATUS // COMPLETE
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-3 text-xs font-mono">
            <div className="p-2 rounded-lg bg-black/40 border border-white/5">
              <div className="text-[10px] text-gray-500 uppercase">Discovered</div>
              <div className="text-base font-bold text-white mt-0.5">{runResult.discovered}</div>
            </div>
            <div className="p-2 rounded-lg bg-black/40 border border-white/5">
              <div className="text-[10px] text-gray-500 uppercase">Matched</div>
              <div className="text-base font-bold text-[#FFB400] mt-0.5">{runResult.matched}</div>
            </div>
            <div className="p-2 rounded-lg bg-black/40 border border-white/5">
              <div className="text-[10px] text-gray-500 uppercase">Eligible</div>
              <div className="text-base font-bold text-emerald-400 mt-0.5">{runResult.eligible}</div>
            </div>
            <div className="p-2 rounded-lg bg-black/40 border border-emerald-500/20 bg-emerald-950/20">
              <div className="text-[10px] text-emerald-400 uppercase">Applied</div>
              <div className="text-base font-bold text-emerald-300 mt-0.5">{runResult.applied}</div>
            </div>
            {runResult.requires_manual_action > 0 && (
              <div className="p-2 rounded-lg bg-black/40 border border-purple-500/20 bg-purple-950/20">
                <div className="text-[10px] text-purple-400 uppercase">Manual Action</div>
                <div className="text-base font-bold text-purple-300 mt-0.5">{runResult.requires_manual_action}</div>
              </div>
            )}
            {runResult.blocked > 0 && (
              <div className="p-2 rounded-lg bg-black/40 border border-orange-500/20 bg-orange-950/20">
                <div className="text-[10px] text-orange-400 uppercase">Blocked</div>
                <div className="text-base font-bold text-orange-300 mt-0.5">{runResult.blocked}</div>
              </div>
            )}
            {runResult.failed > 0 && (
              <div className="p-2 rounded-lg bg-black/40 border border-red-500/20 bg-red-950/20">
                <div className="text-[10px] text-red-400 uppercase">Failed</div>
                <div className="text-base font-bold text-red-300 mt-0.5">{runResult.failed}</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* CENTRAL COMMAND REACTOR & SYSTEM READOUTS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        {/* Left 60%: Central AI Reactor & Visual Anchor */}
        <div className="lg:col-span-7 glass-panel p-6 rounded-2xl border border-[#FF8A00]/20 flex flex-col items-center justify-center relative overflow-hidden group min-h-[380px]">
          {/* Radial ambient background lighting */}
          <div
            className="absolute inset-0 bg-radial from-[#FF8A00]/15 via-transparent to-transparent opacity-80 pointer-events-none"
            aria-hidden="true"
          />

          {/* Reactor Header Telemetry */}
          <div className="w-full flex items-center justify-between border-b border-white/5 pb-3 z-10">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#FFB400] shadow-[0_0_8px_#FFB400]" />
              <span className="font-mono text-xs font-bold text-white uppercase tracking-wider">
                AI CORE // ORBITAL REACTOR
              </span>
            </div>
            <span className="font-mono text-[10px] text-[#FFB400] px-2 py-0.5 rounded bg-[#FF8A00]/10 border border-[#FF8A00]/20">
              SCAN STATE: {reactorState}
            </span>
          </div>

          {/* The AI Reactor Core */}
          <div className="relative z-10 my-4 flex flex-col items-center">
            <AIReactor
              state={reactorState}
              size={280}
              showStatusLabel={true}
              className="glow-amber"
            />
          </div>

          {/* Reactor Subtitle Telemetry */}
          <div className="w-full pt-3 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono text-gray-400 z-10 gap-2">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>SYSTEM INTELLIGENCE: ACTIVE</span>
            </div>
            <div className="text-gray-500">
              {running ? "ANALYZING OPPORTUNITY MATRIX..." : "STANDBY // READY FOR DISCOVERY"}
            </div>
          </div>
        </div>

        {/* Right 40%: System Status & Live Logs */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <AISystemStatus
            isProcessing={running}
            activeModule={running ? "MATCH ENGINE" : undefined}
          />
          <AISystemLog logs={logs} className="flex-1 min-h-[180px]" />
        </div>
      </div>

      {/* KEY METRICS READOUTS */}
      <div>
        <div className="flex items-center justify-between mb-3 px-1">
          <div className="flex items-center gap-2 font-mono text-xs font-semibold text-gray-300 uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FF8A00]" />
            <span>OPERATIONAL METRICS</span>
          </div>
          <span className="font-mono text-[10px] text-gray-500 uppercase">
            REAL-TIME PIPELINE DATA
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3 md:grid-cols-6">
          <StatCard label="Jobs discovered" value={j.length} />
          <StatCard label="Jobs matched" value={j.filter((x) => x.match_score !== null).length} />
          <StatCard label="Applications today" value={todayApps} />
          <StatCard label="Applications submitted" value={count("APPLIED")} />
          <StatCard label="Applications failed" value={count("FAILED")} />
          <StatCard label="Applications blocked" value={count("BLOCKED") + count("REQUIRES_MANUAL_ACTION")} />
        </div>
      </div>

      {/* RECENT APPLICATIONS CONSOLE */}
      <div className="space-y-3">
        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FFB400]" />
            <h2 className="font-sans font-bold text-base text-white">
              Recent applications
            </h2>
          </div>
          <span className="font-mono text-[10px] text-gray-500 uppercase tracking-wider">
            SHOWING LATEST {Math.min(a.length, 5)} OF {a.length}
          </span>
        </div>
        <ApplicationsTable applications={a.slice(0, 5)} />
      </div>
    </div>
  );
}
