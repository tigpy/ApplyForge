import React, { useEffect, useState } from "react";

interface TopBarProps {
  onOpenMobileMenu: () => void;
}

export const TopBar: React.FC<TopBarProps> = ({ onOpenMobileMenu }) => {
  const [time, setTime] = useState<string>("");
  const [aiProvider, setAiProvider] = useState<string>("DETECTING...");

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setTime(
        now.toLocaleTimeString("en-US", {
          hour12: false,
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        })
      );
    };
    update();
    const timer = setInterval(update, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d?.ai_provider) {
          setAiProvider(d.ai_provider.toUpperCase());
        } else {
          setAiProvider("ONLINE");
        }
      })
      .catch(() => setAiProvider("ONLINE"));
  }, []);

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 md:px-8 border-b border-white/5 bg-[#030304]/85 backdrop-blur-xl">
      {/* Left: Mobile trigger & System Identity */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileMenu}
          className="lg:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 focus:outline-none"
          aria-label="Open navigation menu"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        <div className="hidden sm:flex items-center gap-2">
          <span className="font-mono text-xs uppercase tracking-widest text-[#9CA3AF]">
            SYSTEM
          </span>
          <span className="text-gray-700">//</span>
          <span className="font-mono text-xs font-semibold text-[#FFB400] tracking-wider">
            APPLYFORGE 2.0
          </span>
        </div>
      </div>

      {/* Right: Technical Metadata & Telemetry */}
      <div className="flex items-center gap-3 md:gap-5">
        {/* Real AI Provider Indicator */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.03] border border-white/10">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#FFB400] opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#FF8A00]" />
          </span>
          <span className="font-mono text-[11px] text-gray-300 tracking-wide">
            AI CORE: <span className="font-semibold text-[#FFB400]">{aiProvider}</span>
          </span>
        </div>

        {/* System Clock */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/[0.02] border border-white/5 font-mono text-[11px] text-gray-400">
          <svg className="w-3.5 h-3.5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="tracking-widest">{time || "00:00:00"}</span>
        </div>
      </div>
    </header>
  );
};
export default TopBar;
