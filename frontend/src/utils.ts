import { getApiBase } from "./services/api";

export const WHATSAPP_COMMUNITY_URL = "https://chat.whatsapp.com/FszfMQ2sjLf9EyvCaCNh5y";

function shareBaseUrl(): string {
  const apiBase = getApiBase();
  return apiBase.startsWith("http") ? apiBase : `${window.location.origin}${apiBase}`;
}

export function money(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const amount = Number(value);
  if (Number.isNaN(amount)) return String(value);
  return new Intl.NumberFormat("en-NG", { style: "currency", currency: "NGN", maximumFractionDigits: 0 }).format(amount);
}

export function shortDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short", hour12: true }).format(date);
}

export function relativeTime(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const seconds = Math.round((Date.now() - date.getTime()) / 1000);
  if (seconds < 0) return shortDate(value);
  if (seconds < 60) return "Just now";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes} min${minutes === 1 ? "" : "s"} ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  const days = Math.round(hours / 24);
  if (days < 7) return `${days} day${days === 1 ? "" : "s"} ago`;
  return shortDate(value);
}

export function movementIcon(movement: string): string {
  if (movement === "up") return "▲";
  if (movement === "down") return "▼";
  if (movement === "stable") return "●";
  return "–";
}

const HIGH_CONFIDENCE = new Set(["Verified by 2 sources", "Admin confirmed", "Market visit confirmed"]);
const LOW_CONFIDENCE = new Set(["Low confidence", "Price outdated"]);

export function confidenceClass(level: string): string {
  if (HIGH_CONFIDENCE.has(level)) return "confidence-high";
  if (LOW_CONFIDENCE.has(level)) return "confidence-low";
  return "confidence-medium";
}

export function daysUntil(value: string | null | undefined): number | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return Math.ceil((date.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
}

export const STALE_INTELLIGENCE_DAYS = 14;

export function daysSince(value: string | null | undefined): number | null {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24));
}

export function isStale(value: string | null | undefined): boolean {
  const days = daysSince(value);
  return days !== null && days >= STALE_INTELLIGENCE_DAYS;
}

type ShareablePrice = {
  commodity: { name: string };
  market: { name: string };
  price_low: string | number;
  price_high: string | number;
  unit: string;
  bag_size?: string | null;
};

const COMMODITY_EMOJI: Record<string, string> = {
  egusi: "🟡",
  "honey beans": "🟤",
  "palm oil": "🟠",
};

function commodityEmoji(name: string): string {
  return COMMODITY_EMOJI[name.trim().toLowerCase()] || "🌾";
}

export function whatsAppShareUrl(item: ShareablePrice): string {
  const link = `${shareBaseUrl()}/share/commodities/${encodeURIComponent(item.commodity.name)}`;
  const measure = item.bag_size || item.unit;
  const text = `${commodityEmoji(item.commodity.name)} ${item.commodity.name} @ ${item.market.name}: ${money(item.price_low)} – ${money(item.price_high)} (${measure}) — via PriceYard\n${link}`;
  return `https://wa.me/?text=${encodeURIComponent(text)}`;
}

export function referralLink(code: string): string {
  return `${window.location.origin}/register?ref=${encodeURIComponent(code)}`;
}

export function comingSoonShareUrl(commodityName: string): string {
  const text = `${commodityName} is coming soon to PriceYard — great for storage businesses. See real market prices for Egusi, Honey Beans, Palm oil and more.\n${window.location.origin}`;
  return `https://wa.me/?text=${encodeURIComponent(text)}`;
}

export function referralWhatsAppShareUrl(code: string, rewardDays: number): string {
  const text = `Track real agricultural commodity prices with PriceYard — sign up with my link and I get ${rewardDays} extra trial days:\n${referralLink(code)}`;
  return `https://wa.me/?text=${encodeURIComponent(text)}`;
}

export function dateOnly(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("en-NG", { dateStyle: "medium" }).format(date);
}
