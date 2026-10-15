export function supportsAdminPaging(path: string, enabled?: boolean): boolean;
export function adminPagePath(path: string, page?: number, pageSize?: number, enabled?: boolean): string;
export function createLatestRequestGate(): {
  begin(): { signal: AbortSignal; isCurrent: () => boolean };
  cancel(): void;
};
