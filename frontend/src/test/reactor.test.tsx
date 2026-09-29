import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { AIReactor, type ReactorState } from "../components/ai/AIReactor";
import { AISystemStatus } from "../components/ai/AISystemStatus";
import { AppShell } from "../components/shell/AppShell";

describe("Phase UI-1 Design System & Reactor Foundation", () => {
  it("renders AIReactor across different states", () => {
    const states: ReactorState[] = ["IDLE", "SCANNING", "ANALYZING", "MATCHING", "APPLYING", "COMPLETE", "ERROR"];

    states.forEach((state) => {
      const { unmount } = render(<AIReactor state={state} showStatusLabel={true} />);
      expect(screen.getByLabelText(`AI Reactor - State: ${state}`)).toBeInTheDocument();
      expect(screen.getByText(new RegExp(`REACTOR // ${state}`))).toBeInTheDocument();
      unmount();
    });
  });

  it("renders AISystemStatus with core telemetry modules", () => {
    render(<AISystemStatus />);
    expect(screen.getByText("SYSTEM TELEMETRY")).toBeInTheDocument();
    expect(screen.getByText("AI CORE")).toBeInTheDocument();
    expect(screen.getByText("JOB SOURCES")).toBeInTheDocument();
    expect(screen.getByText("RESUME ENGINE")).toBeInTheDocument();
    expect(screen.getByText("MATCH ENGINE")).toBeInTheDocument();
    expect(screen.getByText("APPLICATION ENGINE")).toBeInTheDocument();
  });

  it("renders AppShell with navigation rail and system elements", () => {
    render(
      <MemoryRouter>
        <AppShell>
          <div data-testid="test-content">Workspace Content</div>
        </AppShell>
      </MemoryRouter>
    );

    expect(screen.getByText("ApplyForge")).toBeInTheDocument();
    expect(screen.getByText("Command Center")).toBeInTheDocument();
    expect(screen.getByText("Resume Center")).toBeInTheDocument();
    expect(screen.getByText("Job Intelligence")).toBeInTheDocument();
    expect(screen.getByText("Applications")).toBeInTheDocument();
    expect(screen.getByText("Settings")).toBeInTheDocument();
    expect(screen.getByTestId("test-content")).toBeInTheDocument();
  });
});
