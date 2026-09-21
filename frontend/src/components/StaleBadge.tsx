import { daysSince, isStale } from "../utils";

export function StaleBadge({ updatedAt }: { updatedAt: string | null | undefined }) {
  if (!isStale(updatedAt)) return null;
  const days = daysSince(updatedAt);
  return (
    <span className="stale-badge" title="Not reviewed in a while — check it still matches the current price">
      ⚠ Needs review — {days} days old
    </span>
  );
}
