import React from "react";
import { AppShell } from "./shell/AppShell";

export function Layout() {
  return <AppShell />;
}

export function ErrorNote({ message }: { message: string | null }) {
  return message ? (
    <div
      role="alert"
      className="p-3.5 rounded-xl bg-red-950/50 border border-red-500/30 text-red-300 font-mono text-xs flex items-center gap-2 shadow-[0_0_16px_rgba(239,68,68,0.15)]"
    >
      <span className="w-2 h-2 rounded-full bg-red-500 animate-ping shrink-0" />
      <span>{message}</span>
    </div>
  ) : null;
}
