export function coalescePublicRead<T>(key: string, load: () => Promise<T>): Promise<T>;
