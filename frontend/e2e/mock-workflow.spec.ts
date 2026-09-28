import { expect, test } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const fixture = path.join(path.dirname(fileURLToPath(import.meta.url)), "fixtures", "cybersecurity.pdf");

test("mock workflow: upload -> discover -> match -> apply -> APPLIED + notification", async ({ page, request }) => {
  // Candidate profile (normally filled on the Settings page).
  const put = await request.put("/api/profile", {
    data: { name: "Test Candidate", email: "test@example.com", phone: "+1 555 0100" },
  });
  expect(put.ok()).toBeTruthy();

  // 1. Upload resume
  await page.goto("/resumes");
  await page.getByTestId("resume-file").setInputFiles(fixture);
  await page.getByRole("button", { name: "Upload" }).click();
  await expect(page.getByTestId("resume-list")).toContainText("cybersecurity.pdf");

  // 2. Discover mock jobs
  await page.goto("/jobs");
  await page.getByRole("button", { name: "Discover jobs" }).click();
  await page.getByRole("link", { name: /Junior Security Analyst/ }).click();

  // 3. Match -> best resume selected
  await page.getByRole("button", { name: "Run match" }).click();
  await expect(page.getByTestId("match-resume")).toHaveText("cybersecurity.pdf");
  await expect(page.getByTestId("match-recommendation")).toHaveText("APPLY");

  // 4. Apply through the mock connector -> APPLIED
  await page.getByRole("button", { name: "Apply now" }).click();
  await expect(page.getByTestId("application-status")).toHaveText("APPLIED");

  // 5. Notification generated and recorded
  await expect(page.getByTestId("event-list")).toContainText("NOTIFIED");
  await expect(page.getByTestId("event-list")).toContainText("Applied Successfully");

  // History shows it
  await page.goto("/applications");
  await expect(page.getByTestId("applications-table")).toContainText("Example Corp");
  await expect(page.getByTestId("applications-table")).toContainText("APPLIED");
});

test("automation run: Run Job Search executes full pipeline from dashboard", async ({ page, request }) => {
  await request.put("/api/profile", {
    data: {
      name: "Aryan Sharma",
      email: "aryan@example.com",
      phone: "+91 9876543210",
      facts: { work_authorization: "Yes" },
    },
  });

  await page.goto("/resumes");
  await page.getByTestId("resume-file").setInputFiles(fixture);
  await page.getByRole("button", { name: "Upload" }).click();
  await expect(page.getByTestId("resume-list")).toContainText("cybersecurity.pdf");

  // Verify text preview toggle works
  await page.getByRole("button", { name: "Preview text" }).click();
  await expect(page.getByTestId("resume-list")).toContainText("Python");

  // Navigate to Dashboard and click Run Job Search
  await page.goto("/");
  await page.getByRole("button", { name: "Run Job Search" }).click();

  // Summary banner should appear
  await expect(page.getByText("Automation Run Completed:")).toBeVisible();

  // Check applications table
  await expect(page.getByTestId("applications-table")).toContainText("Example Corp");
  await expect(page.getByTestId("applications-table")).toContainText("APPLIED");
});
