// Explicitly verified list endpoints; catalog and FAQ reads remain unchanged.
const pagedLists = new Set([
  "/users", "/subscriptions", "/audit-logs", "/feedback",
  "/price-updates/admin/history", "/price-updates/admin/flagged",
  "/market-signals", "/quality-signals", "/buying-zones",
  "/sell-watch-windows", "/storage-suitability", "/cost-breakdowns",
]);

export function supportsAdminPaging(path, enabled = true) {
  return enabled && pagedLists.has(path.split("?")[0]);
}

export function adminPagePath(path, page = 1, pageSize = 100, enabled = true) {
  if (!supportsAdminPaging(path, enabled)) return path;
  if (!Number.isInteger(page) || page < 1 || !Number.isInteger(pageSize) || pageSize < 1 || pageSize > 1000) {
    throw new RangeError("Invalid administrative page bounds");
  }
  const [base, query = ""] = path.split("?", 2);
  const parameters = new URLSearchParams(query);
  parameters.set("page", String(page));
  parameters.set("page_size", String(pageSize));
  return `${base}?${parameters}`;
}

export function createLatestRequestGate() {
  let generation = 0;
  let controller;
  return {
    begin() {
      generation += 1;
      controller?.abort();
      controller = new AbortController();
      const current = generation;
      const signal = controller.signal;
      return { signal, isCurrent: () => current === generation && !signal.aborted };
    },
    cancel() { generation += 1; controller?.abort(); },
  };
}
