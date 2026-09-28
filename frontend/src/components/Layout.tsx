import { NavLink, Outlet } from "react-router-dom";

const links = [
  ["/", "Dashboard"], ["/resumes", "Resumes"], ["/jobs", "Jobs"],
  ["/applications", "Applications"], ["/settings", "Settings"],
] as const;

export function Layout() {
  return (
    <div className="min-h-screen">
      <header className="border-b bg-white">
        <nav className="mx-auto flex max-w-5xl items-center gap-6 p-4">
          <span className="text-lg font-bold">ApplyForge</span>
          {links.map(([to, label]) => (
            <NavLink key={to} to={to} end={to === "/"}
              className={({ isActive }) => (isActive ? "font-semibold text-blue-700" : "text-slate-600 hover:text-slate-900")}>
              {label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="mx-auto max-w-5xl space-y-4 p-4"><Outlet /></main>
    </div>
  );
}

export function ErrorNote({ message }: { message: string | null }) {
  return message ? <p role="alert" className="rounded bg-red-50 p-2 text-sm text-red-700">{message}</p> : null;
}
