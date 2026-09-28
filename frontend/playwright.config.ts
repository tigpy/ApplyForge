import { defineConfig } from "@playwright/test";

// Starts a fresh backend (mock connectors, throw-away DB in data/) and the Vite dev server.
// Prerequisite: backend venv is ACTIVATED so `python` has the backend requirements, and
// `npx playwright install chromium` has been run once.
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  use: { baseURL: "http://localhost:5173" },
  webServer: [
    {
      command: "python -m uvicorn app.main:app --port 8000",
      cwd: "../backend",
      url: "http://127.0.0.1:8000/api/health",
      reuseExistingServer: false,
      env: {
        DATABASE_URL: "sqlite:///./data/e2e.db",
        RESUME_DIR: "./data/e2e-resumes",
        AI_PROVIDER: "mock",
        APPLICATION_CONNECTOR: "mock",
        NOTIFICATION_MODE: "mock",
      },
    },
    { command: "npm run dev -- --strictPort", url: "http://localhost:5173", reuseExistingServer: false },
  ],
});
