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
