type NamedRecord = { id: number; name: string };

export const identityValue = (id: number) => `id:${id}`;
export const nameSelection = (name: string) => name ? `name:${name}` : "";

export function selectionFromQuery(query: URLSearchParams, key: "commodity" | "market"): string {
  return query.has(`${key}_id`) ? `id:${query.get(`${key}_id`)}` : nameSelection(query.get(key) || "");
}

export function selectedIdentity(value: string, records: NamedRecord[]): string {
  if (value.startsWith("id:")) return value;
  const name = value.startsWith("name:") ? value.slice(5) : value;
  const matches = records.filter((record) => record.name === name);
  return matches.length === 1 ? identityValue(matches[0].id) : value;
}

export function identityLabel(value: string, records: NamedRecord[]): string {
  return value.startsWith("id:")
    ? records.find((record) => identityValue(record.id) === value)?.name || ""
    : value.startsWith("name:") ? value.slice(5) : value;
}

export function addIdentityFilter(query: URLSearchParams, key: "commodity" | "market", value?: string): void {
  if (!value) return;
  if (value.startsWith("id:")) query.set(`${key}_id`, value.slice(3));
  else query.set(key, value.startsWith("name:") ? value.slice(5) : value);
}

export function commodityLink(record: NamedRecord): string {
  return `/commodities/${encodeURIComponent(record.name)}?commodity_id=${record.id}`;
}
