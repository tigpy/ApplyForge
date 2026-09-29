import React, { useEffect, useRef } from "react";

export interface LogEntry {
  id: string;
  time: string;
  message: string;
  level?: "INFO" | "WARN" | "SUCCESS" | "AI";
}

interface AISystemLogProps {
  logs: LogEntry[];
  className?: string;
  title?: string;
}

export const AISystemLog: React.FC<AISystemLogProps> = ({
  logs,
  className = "",
  title = "LIVE TELEMETRY // AI LOG",
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className={`glass-panel rounded-xl border border-white/5 flex flex-col ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/5 bg-white/[0.01]">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-[#FFB400] animate-pulse" />
          <span className="font-mono text-[10px] font-semibold text-gray-300 uppercase tracking-widest">
            {title}
          </span>
        </div>
        <span className="font-mono text-[9px] text-[#6B7280] tracking-wider uppercase">
          LOG STREAM // AUTO-SYNC
        </span>
      </div>

      {/* Log Terminal Window */}
      <div
        ref={scrollRef}
        className="p-3 space-y-1.5 font-mono text-[11px] max-h-48 overflow-y-auto select-text scroll-smooth"
      >
        {logs.map((log) => {
          const isSuccess = log.level === "SUCCESS";
          const isAi = log.level === "AI";
          const isWarn = log.level === "WARN";

          return (
            <div
              key={log.id}
              className="flex items-start gap-2 leading-relaxed hover:bg-white/[0.02] px-1 rounded transition-colors"
            >
              <span className="text-gray-500 shrink-0 select-none">
                [{log.time}]
              </span>
              <span
                className={`break-all ${
                  isSuccess
                    ? "text-emerald-400 font-medium"
                    : isAi
                    ? "text-[#FFB400] font-semibold"
                    : isWarn
                    ? "text-amber-400"
                    : "text-gray-300"
                }`}
              >
                {log.message}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
export default AISystemLog;
