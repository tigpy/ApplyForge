import React, { useState } from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

interface AppShellProps {
  children?: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-[#020203] text-gray-100 flex flex-col font-sans selection:bg-[#FF8A00]/30 selection:text-[#FFB400]">
      {/* Background ambient lighting */}
      <div
        className="fixed inset-0 pointer-events-none bg-reactor-grid opacity-60 z-0"
        aria-hidden="true"
      />
      <div
        className="fixed top-0 left-1/3 w-[500px] h-[500px] bg-[#FF8A00]/5 rounded-full blur-[140px] pointer-events-none z-0"
        aria-hidden="true"
      />

      {/* Navigation Sidebar */}
      <Sidebar isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />

      {/* Workspace Area offset by sidebar width on desktop */}
      <div className="flex-1 flex flex-col lg:pl-64 z-10">
        <TopBar onOpenMobileMenu={() => setMobileMenuOpen(true)} />

        {/* Main Content Area */}
        <main className="flex-1 px-4 py-6 md:px-8 md:py-8 max-w-7xl w-full mx-auto space-y-6">
          {children || <Outlet />}
        </main>

        {/* Global Technical Footer */}
        <footer className="py-4 px-6 md:px-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-[11px] font-mono text-gray-600 gap-2">
          <div className="flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FFB400]" />
            <span>APPLYFORGE INTELLIGENCE PLATFORM</span>
          </div>
          <div>STATUS: ALL SYSTEMS NOMINAL // REST API CONNECTED</div>
        </footer>
      </div>
    </div>
  );
};
export default AppShell;
