import React from "react";
import { NavLink } from "react-router-dom";

export interface NavItem {
  to: string;
  label: string;
  tag: string;
  icon: (props: { className?: string }) => React.JSX.Element;
}

const navItems: NavItem[] = [
  {
    to: "/",
    label: "Command Center",
    tag: "SYS//01",
    icon: ({ className }) => (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
      </svg>
    ),
  },
  {
    to: "/resumes",
    label: "Resume Center",
    tag: "RES//02",
    icon: ({ className }) => (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
      </svg>
    ),
  },
  {
    to: "/jobs",
    label: "Job Intelligence",
    tag: "JOB//03",
    icon: ({ className }) => (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
      </svg>
    ),
  },
  {
    to: "/applications",
    label: "Applications",
    tag: "APP//04",
    icon: ({ className }) => (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
      </svg>
    ),
  },
  {
    to: "/settings",
    label: "Settings",
    tag: "CFG//05",
    icon: ({ className }) => (
      <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.75}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6h9.75M10.5 6a1.5 1.5 0 11-3 0m3 0a1.5 1.5 0 10-3 0M3.75 6H7.5m3 12h9.75m-9.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-3.75 0H7.5m9-6h3.75m-3.75 0a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m-9.75 0h9.75" />
      </svg>
    ),
  },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Main Sidebar Rail */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col w-64 bg-[#050608]/95 border-r border-[#FF8A00]/15 backdrop-blur-xl transition-transform duration-300 lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between h-18 px-5 border-b border-white/5">
          <div className="flex items-center gap-3">
            {/* Forge Monogram / Reactor icon */}
            <div className="relative flex items-center justify-center w-9 h-9 rounded-lg bg-[#FF8A00]/10 border border-[#FFB400]/40 shadow-[0_0_12px_rgba(255,180,0,0.2)]">
              <span className="font-mono text-sm font-black text-[#FFB400] tracking-tighter">
                AF
              </span>
              <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-[#FF8A00] animate-ping" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-sans text-base font-extrabold tracking-tight text-white">
                  ApplyForge
                </span>
                <span className="px-1.5 py-0.2 rounded font-mono text-[9px] font-bold bg-[#FF8A00]/20 text-[#FFB400] border border-[#FF8A00]/30">
                  v2.0
                </span>
              </div>
              <span className="block font-mono text-[9px] text-[#6B7280] tracking-wider uppercase">
                AUTONOMOUS SYSTEM
              </span>
            </div>
          </div>

          {/* Close button for mobile */}
          {onClose && (
            <button
              onClick={onClose}
              className="lg:hidden p-1.5 text-gray-400 hover:text-white rounded-lg hover:bg-white/5"
              aria-label="Close navigation menu"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
          <div className="px-3 pb-2 text-[10px] font-mono font-semibold uppercase tracking-widest text-[#6B7280]">
            NAVIGATION CORE
          </div>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              onClick={() => onClose && onClose()}
              className={({ isActive }) =>
                `group relative flex items-center justify-between px-3.5 py-2.5 rounded-xl font-medium text-xs transition-all duration-200 ${
                  isActive
                    ? "bg-[#FF8A00]/15 text-white border border-[#FFB400]/40 shadow-[0_0_16px_rgba(255,138,0,0.15)]"
                    : "text-gray-400 hover:text-gray-200 hover:bg-white/[0.03] border border-transparent"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <div className="flex items-center gap-3">
                    <item.icon
                      className={`w-4 h-4 transition-colors ${
                        isActive ? "text-[#FFB400]" : "text-gray-500 group-hover:text-gray-300"
                      }`}
                    />
                    <span className="font-sans text-xs tracking-wide">{item.label}</span>
                  </div>
                  <span
                    className={`font-mono text-[9px] tracking-wider transition-colors ${
                      isActive ? "text-[#FFB400] font-semibold" : "text-gray-600"
                    }`}
                  >
                    {item.tag}
                  </span>

                  {/* Left glowing edge highlight */}
                  {isActive && (
                    <span className="absolute left-0 top-2 bottom-2 w-0.5 rounded-r bg-[#FFB400] shadow-[0_0_8px_#FFB400]" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer Reactor Status Badge */}
        <div className="p-4 mx-3 mb-4 rounded-xl border border-white/5 bg-white/[0.02]">
          <div className="flex items-center justify-between mb-2">
            <span className="font-mono text-[10px] uppercase tracking-wider text-gray-400">
              AUTONOMOUS MODE
            </span>
            <span className="flex items-center gap-1.5 font-mono text-[10px] text-[#FFB400]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#FFB400] animate-pulse" />
              ONLINE
            </span>
          </div>
          <div className="w-full bg-white/10 rounded-full h-1 overflow-hidden">
            <div className="bg-gradient-to-r from-[#FF5A00] to-[#FFB400] h-full w-[85%] rounded-full animate-pulse" />
          </div>
          <div className="mt-2 flex items-center justify-between text-[9px] font-mono text-gray-500">
            <span>CORE: STABLE</span>
            <span>44.1 KHZ</span>
          </div>
        </div>
      </aside>
    </>
  );
};
export default Sidebar;
