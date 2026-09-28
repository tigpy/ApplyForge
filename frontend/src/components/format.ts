/** Backend sends naive UTC timestamps; add "Z" so the browser converts to local time. */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "-";
  const d = new Date(/[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : iso + "Z");
  return d.toLocaleDateString(undefined, { day: "2-digit", month: "short", year: "numeric" });
}
