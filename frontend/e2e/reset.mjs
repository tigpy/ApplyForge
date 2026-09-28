// Removes the throw-away E2E database and uploads so every run starts clean.
import { rmSync } from "node:fs";
import { fileURLToPath } from "node:url";

const data = fileURLToPath(new URL("../../data/", import.meta.url));
for (const name of ["e2e.db", "e2e.db-wal", "e2e.db-shm", "e2e-resumes"]) {
  rmSync(data + name, { recursive: true, force: true });
}
console.log("E2E data reset");
