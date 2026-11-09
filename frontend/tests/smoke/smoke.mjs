// Website page checks (owner-approved audit item 11, step 1).
// Opens every page on a phone-sized and a desktop-sized screen, as a visitor and
// as an admin, with fake server answers (no real data, no network). Fails if any
// page shows a script error, comes up blank, or has content cut off at the screen edge.
//
// Usage: SMOKE_BASE_URL=http://127.0.0.1:4322 node smoke.mjs
// (SMOKE_BROWSER_CHANNEL=msedge uses an installed Edge instead of Playwright's Chromium.)
import { chromium } from "playwright";

const BASE = (process.env.SMOKE_BASE_URL || "http://127.0.0.1:4322").replace(/\/$/, "");
const CHANNEL = process.env.SMOKE_BROWSER_CHANNEL || undefined;

const PUBLIC_PAGES = ["/", "/prices", "/prices?market=Kwali%20Market", "/commodities/Egusi", "/history", "/market-days",
  "/faq", "/about", "/login", "/register", "/forgot-password", "/no-such-page"];
const MEMBER_PAGES = ["/dashboard", "/watchlist", "/feedback", "/report-price"];
const ADMIN_PAGES = ["/admin", "/admin/activity", "/admin/users", "/admin/commodities", "/admin/markets", "/admin/prices",
  "/admin/flagged", "/admin/market-signals", "/admin/quality-signals", "/admin/buying-zones", "/admin/sell-watch",
  "/admin/costs", "/admin/faq", "/admin/subscriptions", "/admin/payments", "/admin/feedback", "/admin/audit", "/admin/export"];

const COMMODITIES = [{ id: 1, name: "Egusi", is_active: true, is_upcoming: false }];
const MARKETS = [{ id: 12, name: "Kwali Market", is_active: true, market_day: "Friday", state: "FCT" }];
const ADMIN = { id: 31, email: "admin@example.com", full_name: "Test Admin", role: "admin", is_active: true };

function fakeServer(signedIn) {
  return async (route) => {
    const path = new URL(route.request().url()).pathname.replace(/^\/api/, "");
    const json = (body, status = 200) => route.fulfill({ status, json: body });
    if (path === "/auth/browser/session") return signedIn ? json({ session_id: "s1", csrf_token: "c1" }) : json({ detail: "Not authenticated" }, 401);
    if (path === "/auth/me") return signedIn ? json(ADMIN) : json({ detail: "Not authenticated" }, 401);
    if (path.startsWith("/subscriptions/")) return json({ status: "active", plan_name: "paid_monthly" });
    if (path === "/commodities") return json(COMMODITIES);
    if (path === "/markets") return json(MARKETS);
    if (path.endsWith("/page")) return json({ items: [], total: 0, offset: 0, limit: 20 });
    if (path.includes("admin/summary")) return json({});
    if (path === "/activity/summary") return json({ unseen_count: 0, recent: [] });
    return json([]);
  };
}

async function waitForSite() {
  for (let i = 0; i < 60; i += 1) {
    try { if ((await fetch(BASE + "/")).ok) return; } catch { /* not up yet */ }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`Website did not start at ${BASE}`);
}

async function checkPages(browser, { width, signedIn, pages }) {
  const page = await browser.newPage({ viewport: { width, height: 800 }, serviceWorkers: "block" });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error" && !/Failed to load resource/.test(message.text())) errors.push(message.text());
  });
  await page.addInitScript(() => { try { localStorage.setItem("priceyard_onboarding_seen", "1"); } catch { /* ignore */ } });
  await page.route(/\/api\//, fakeServer(signedIn));

  const problems = [];
  for (const url of pages) {
    errors.length = 0;
    await page.goto(BASE + url, { waitUntil: "load" });
    await page.waitForTimeout(700);
    const state = await page.evaluate(() => {
      const main = document.querySelector("main");
      // The site clips sideways overflow, so look for content that runs past the
      // screen edge (it would be cut off), except inside areas meant to scroll.
      const scrolls = (el) => {
        for (let node = el.parentElement; node && node !== main; node = node.parentElement) {
          const overflow = getComputedStyle(node).overflowX;
          if (overflow === "auto" || overflow === "scroll" || overflow === "hidden") return true;
        }
        return false;
      };
      let cutOff = null;
      for (const el of main ? main.querySelectorAll("*") : []) {
        const box = el.getBoundingClientRect();
        if (box.width === 0 || box.height === 0) continue;
        if ((box.right > window.innerWidth + 1 || box.left < -1) && !scrolls(el)) {
          cutOff = `${el.tagName.toLowerCase()}${el.className && typeof el.className === "string" ? "." + el.className.split(" ")[0] : ""}`;
          break;
        }
      }
      return { blank: !main || main.innerText.trim().length < 5, cutOff };
    });
    const label = `${signedIn ? "admin" : "visitor"} ${width}px ${url}`;
    if (errors.length) problems.push(`${label}: script error: ${errors[0].slice(0, 160)}`);
    if (state.blank) problems.push(`${label}: page is blank`);
    if (state.cutOff) problems.push(`${label}: content runs past the screen edge (${state.cutOff})`);
  }

  if (signedIn) {
    // The top links must lead somewhere, and the browser Back button must return.
    await page.goto(BASE + "/", { waitUntil: "load" });
    await page.waitForTimeout(500);
    await page.locator("#priceyard-primary-navigation a", { hasText: "Help" }).first().click();
    await page.waitForTimeout(400);
    const afterClick = await page.evaluate(() => location.pathname);
    await page.goBack();
    await page.waitForTimeout(400);
    const afterBack = await page.evaluate(() => location.pathname);
    if (afterClick !== "/faq" || afterBack !== "/") problems.push(`admin ${width}px top links: Help -> ${afterClick}, back -> ${afterBack}`);
  }
  await page.close();
  return problems;
}

await waitForSite();
const browser = await chromium.launch(CHANNEL ? { channel: CHANNEL } : {});
const problems = [];
let checked = 0;
try {
  for (const width of [375, 1280]) {
    problems.push(...await checkPages(browser, { width, signedIn: false, pages: PUBLIC_PAGES }));
    const all = [...PUBLIC_PAGES, ...MEMBER_PAGES, ...ADMIN_PAGES];
    problems.push(...await checkPages(browser, { width, signedIn: true, pages: all }));
    checked += PUBLIC_PAGES.length + all.length;
  }
} finally {
  await browser.close();
}

if (problems.length) {
  console.error(`Website page checks FAILED (${problems.length} problem(s)):`);
  for (const problem of problems) console.error(" - " + problem);
  process.exit(1);
}
console.log(`Website page checks passed: ${checked} page views (phone and desktop, visitor and admin).`);
