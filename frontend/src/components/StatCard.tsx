import React from "react";

export function StatCard({ label, value }: { label: string; value: number | string }) {
  const formattedVal =
    typeof value === "number" && value < 1000
      ? String(value).padStart(3, "0")
      : String(value);

  return (
    <div className="glass-panel p-4 rounded-xl border border-white/5 hover:border-[#FF8A00]/30 transition-all duration-300 relative group overflow-hidden">
      {/* Corner mechanical indicator */}
      <span className="absolute top-0 right-0 w-2 h-2 border-t border-r border-[#FFB400]/40 group-hover:border-[#FFB400] transition-colors" />

      <div className="flex flex-col justify-between h-full">
        <div className="text-[10px] md:text-[11px] font-mono font-medium tracking-wider text-gray-400 uppercase">
          {label}
        </div>
        <div className="mt-2 flex items-baseline justify-between">
          <span className="font-mono text-2xl md:text-3xl font-extrabold text-white tracking-tight group-hover:text-[#FFB400] transition-colors">
            {formattedVal}
          </span>
          <span className="w-1.5 h-1.5 rounded-full bg-[#FFB400]/40 group-hover:bg-[#FFB400] transition-colors" />
        </div>
      </div>
    </div>
  );
}
