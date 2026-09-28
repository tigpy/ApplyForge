import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { ApplicationsTable } from "../components/ApplicationsTable";
import { JobList } from "../components/JobList";
import { ResumeList } from "../components/ResumeList";
import { StatusBadge } from "../components/StatusBadge";
import Dashboard from "../pages/Dashboard";
import { application, job, resume } from "./fixtures";

vi.mock("../services/api", async () => {
  const f = await import("./fixtures");
  return {
    api: {
      listJobs: vi.fn().mockResolvedValue([f.job]),
      listApplications: vi.fn().mockResolvedValue([f.application, { ...f.application, id: 2, status: "BLOCKED" }]),
    },
  };
});

const wrap = (ui: React.ReactNode) => render(<MemoryRouter>{ui}</MemoryRouter>);

describe("skeleton UI", () => {
  it("dashboard renders stats and recent applications", async () => {
    wrap(<Dashboard />);
    expect(await screen.findByText("Jobs discovered")).toBeInTheDocument();
    expect(await screen.findByText("Applications blocked")).toBeInTheDocument();
    expect((await screen.findAllByText("Example Corp")).length).toBe(2);
  });

  it("resume list renders", () => {
    wrap(<ResumeList resumes={[resume]} />);
    expect(screen.getByText("cybersecurity.pdf")).toBeInTheDocument();
  });

  it("job list renders with match score", () => {
    wrap(<JobList jobs={[job]} />);
    expect(screen.getByText(/Junior Security Analyst/)).toBeInTheDocument();
    expect(screen.getByText("91%")).toBeInTheDocument();
  });

  it("application status renders", () => {
    render(<StatusBadge status="BLOCKED" />);
    expect(screen.getByText("BLOCKED")).toBeInTheDocument();
    wrap(<ApplicationsTable applications={[application]} />);
    expect(screen.getByText("APPLIED")).toBeInTheDocument();
  });
});
