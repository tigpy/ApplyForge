import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { ApplicationsTable } from "../components/ApplicationsTable";
import { JobList } from "../components/JobList";
import JobDetail from "../pages/JobDetail";
import type { Job } from "../types";
import { application, job } from "./fixtures";

const { mockJobDetail } = vi.hoisted(() => {
  const mockJob = {
    id: 1,
    company: "Example Corp",
    title: "Junior Security Analyst",
    location: "Toronto",
    remote_type: "hybrid",
    url: "",
    application_url: "",
    source: "mock",
    requirements: ["Python"],
    discovered_at: "2026-09-28T08:00:00",
    status: "ELIGIBLE" as const,
    match_score: 91,
    selected_resume_id: 1,
    selected_resume_name: "cybersecurity.pdf",
    application_id: 1,
    description: "Test job description for junior security analyst.",
    match: {
      job_id: 1,
      score: 91,
      recommendation: "APPLY" as const,
      strengths: ["Python", "SIEM"],
      missing_requirements: [],
      matched_skills: ["Python", "SIEM"],
      missing_skills: [],
      matched_certifications: [],
      role_match: true,
      experience_match: true,
      explanation: "Selected cybersecurity.pdf: matched 2 skill(s) (python, siem); role alignment confirmed.",
      application_id: 1,
      application_status: "ELIGIBLE" as const,
      selected_resume_id: 1,
      selected_resume_name: "cybersecurity.pdf",
      resume_scores: [
        { resume_id: 1, resume_name: "cybersecurity.pdf", score: 91 },
        { resume_id: 2, resume_name: "backend.pdf", score: 45 },
      ],
    },
  };
  return { mockJobDetail: mockJob };
});

vi.mock("../services/api", () => ({
  api: {
    getJob: vi.fn().mockImplementation((id: number) => {
      if (id === 99) {
        return Promise.resolve({
          ...mockJobDetail,
          id: 99,
          status: "APPLIED",
          match: { ...mockJobDetail.match, application_status: "APPLIED" },
        });
      }
      return Promise.resolve(mockJobDetail);
    }),
    matchJob: vi.fn().mockResolvedValue(mockJobDetail.match),
    applyJob: vi.fn().mockResolvedValue({ id: 1, status: "APPLIED" }),
  },
}));

describe("Phase 4B Frontend Tests", () => {
  it("renders job cards with role, company, match score, and best resume", () => {
    render(
      <MemoryRouter>
        <JobList jobs={[job]} />
      </MemoryRouter>
    );

    expect(screen.getByText(/Junior Security Analyst/)).toBeInTheDocument();
    expect(screen.getByText(/Example Corp/)).toBeInTheDocument();
    expect(screen.getByText("91%")).toBeInTheDocument();
    expect(screen.getByText(/Best Resume: cybersecurity\.pdf/)).toBeInTheDocument();
    expect(screen.getByText("ELIGIBLE")).toBeInTheDocument();
  });

  it("renders job detail page with complete match breakdown", async () => {
    render(
      <MemoryRouter initialEntries={["/jobs/1"]}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText("Junior Security Analyst")).toBeInTheDocument();
    expect(screen.getByTestId("match-score")).toHaveTextContent("91%");
    expect(screen.getByTestId("match-resume")).toHaveTextContent("cybersecurity.pdf");
    expect(screen.getByTestId("match-recommendation")).toHaveTextContent("APPLY");
    expect(screen.getByText("Matched Skills:")).toBeInTheDocument();
    expect(screen.getByText("Missing Requirements:")).toBeInTheDocument();
    expect(screen.getByText(/All evaluated resumes:/)).toBeInTheDocument();
    expect(screen.getByText(/cybersecurity\.pdf \(91%\)/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Match" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Apply" })).toBeInTheDocument();
  });

  it("renders applied state banner on job detail when already applied", async () => {
    render(
      <MemoryRouter initialEntries={["/jobs/99"]}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );

    const banner = await screen.findByText(/✓ Applied · Resume used:/);
    expect(banner).toBeInTheDocument();
    expect(banner).toHaveTextContent("cybersecurity.pdf");
    expect(screen.queryByRole("button", { name: "Apply" })).not.toBeInTheDocument();
  });

  it("renders applications table with status, company, role, and resume name", () => {
    render(
      <MemoryRouter>
        <ApplicationsTable applications={[application]} />
      </MemoryRouter>
    );

    expect(screen.getByText("Example Corp")).toBeInTheDocument();
    expect(screen.getByText("Junior Security Analyst")).toBeInTheDocument();
    expect(screen.getByText("cybersecurity.pdf")).toBeInTheDocument();
    expect(screen.getByText("APPLIED")).toBeInTheDocument();
    expect(screen.getByText("91%")).toBeInTheDocument();
  });
});
