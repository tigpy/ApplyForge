import React, { useEffect, useState } from "react";

interface SystemModule {
  name: string;
  code: string;
  status: "ONLINE" | "READY" | "BUSY" | "STANDBY";
  latency?: string;
}

interface AISystemStatusProps {
  activeModule?: string;
  isProcessing?: boolean;
  className?: string;
}

export const AISystemStatus: React.FC<AISystemStatusProps> = ({
  activeModule,
  isProcessing = false,
  className = "",
}) => {
  const [aiProvider, setAiProvider] = useState<string>("DETECTING...");

  useEffect(() => {
    // Probe backend health to see real active AI provider
    fetch("/api/health")
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.ai_provider) {
          setAiProvider(data.ai_provider.toUpperCase());
        } else {
          setAiProvider("ONLINE");
        }
      })
      .catch(() => setAiProvider("STANDBY"));
  }, []);

  const modules: SystemModule[] = [
    { name: "AI CORE", code: `PROVIDER // ${aiProvider}`, status: "ONLINE", latency: "14ms" },
    { name: "JOB SOURCES", code: "DISCOVERY FEED", status: "ONLINE", latency: "38ms" },
    { name: "RESUME ENGINE", code: "PyMuPDF PARSER", status: "READY", latency: "2ms" },
    { name: "MATCH ENGINE", code: "HYBRID VECTOR", status: isProcessing ? "BUSY" : "READY" },
    { name: "APPLICATION ENGINE", code: "PLAYWRIGHT ATS", status: "READY" },
  ];

  return (
    <div className={`glass-panel p-4 rounded-xl border border-[#FF8A00]/20 ${className}`}>
      <div className="flex items-center justify-between pb-3 border-b border-white/5">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#FFB400] opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#FF8A00]" />
          </span>
          <span className="font-mono text-xs font-semibold text-[#FFB400] tracking-widest uppercase">
            SYSTEM TELEMETRY
          </span>
        </div>
        <span className="font-mono text-[10px] text-gray-500 tracking-wider">
          FREQ 44.1 KHZ
        </span>
      </div>

      <div className="mt-3 space-y-2.5">
        {modules.map((m) => {
          const isActive = activeModule === m.name || (isProcessing && m.name === "MATCH ENGINE");
          return (
            <div
              key={m.name}
              className={`flex items-center justify-between p-2 rounded-lg transition-colors ${
                isActive
                  ? "bg-[#FF8A00]/10 border border-[#FFB400]/30"
                  : "bg-white/[0.02] border border-transparent hover:border-white/5"
              }`}
            >
              <div className="flex flex-col">
                <span className="font-mono text-[11px] font-semibold text-gray-200">
                  {m.name}
                </span>
                <span className="font-mono text-[9px] text-gray-500 uppercase tracking-wider">
                  {m.code}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`inline-block w-1.5 h-1.5 rounded-full ${
                    m.status === "ONLINE" || m.status === "READY"
                      ? "bg-[#FFB400] shadow-[0_0_6px_#FFB400]"
                      : m.status === "BUSY"
                      ? "bg-[#FF5A00] animate-pulse"
                      : "bg-gray-600"
                  }`}
                />
                <span className="font-mono text-[10px] text-gray-300 font-medium">
                  {m.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default AISystemStatus;
