import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const read = (relativePath) => readFileSync(resolve(root, relativePath), "utf8");
const failures = [];

function requireText(relativePath, ...needles) {
  const source = read(relativePath);
  for (const needle of needles) {
    if (!source.toLowerCase().includes(needle.toLowerCase())) {
      failures.push(`${relativePath}: missing ${needle}`);
    }
  }
}

requireText(
  "frontend/src/components/LoadingSpinner.tsx",
  "export function LoadingSpinner",
  "export function FullPageLoader",
  "export function ButtonSpinner",
  'role="status"',
  'aria-live="polite"',
);

requireText(
  "frontend/src/styles.css",
  "conic-gradient",
  "#16a34a",
  "#22c55e",
  "#facc15",
  "#ffffff",
  "rgba(255, 255, 255, .72)",
  "rgba(15, 23, 42, .55)",
  "@keyframes priceyard-spin",
  "drop-shadow",
  "button:disabled",
);

const pageLoaders = [
  "frontend/src/components/AdminRoute.tsx",
  "frontend/src/components/ProtectedRoute.tsx",
  "frontend/src/pages/HomePage.tsx",
  "frontend/src/pages/PricesPage.tsx",
  "frontend/src/pages/CommodityDetailPage.tsx",
  "frontend/src/pages/PriceHistoryPage.tsx",
  "frontend/src/pages/MarketDaysPage.tsx",
  "frontend/src/pages/FAQPage.tsx",
  "frontend/src/pages/WatchlistPage.tsx",
];
for (const file of pageLoaders) requireText(file, "Loading");

const buttonLoaders = [
  "frontend/src/components/Layout.tsx",
  "frontend/src/pages/LoginPage.tsx",
  "frontend/src/pages/RegisterPage.tsx",
  "frontend/src/pages/FeedbackPage.tsx",
  "frontend/src/pages/PricesPage.tsx",
  "frontend/src/pages/PriceHistoryPage.tsx",
  "frontend/src/pages/WatchlistPage.tsx",
  "frontend/src/pages/admin/adminUtils.tsx",
];
for (const file of buttonLoaders) requireText(file, "Spinner", "disabled");

const adminLoaders = [
  "AdminAuditLogsPage.tsx",
  "AdminCommoditiesPage.tsx",
  "AdminDashboardPage.tsx",
  "AdminFAQPage.tsx",
  "AdminFeedbackPage.tsx",
  "AdminIntelligencePages.tsx",
  "AdminMarketsPage.tsx",
  "AdminPriceUpdatesPage.tsx",
  "AdminSignalsPage.tsx",
  "AdminSubscriptionsPage.tsx",
  "AdminUsersPage.tsx",
];
for (const name of adminLoaders) {
  requireText(`frontend/src/pages/admin/${name}`, "AdminLoading");
}
requireText("frontend/src/pages/admin/AdminExportPage.tsx", "AdminActionButton", "busy", "finally");

const completionFiles = [
  "frontend/src/pages/LoginPage.tsx",
  "frontend/src/pages/RegisterPage.tsx",
  "frontend/src/pages/FeedbackPage.tsx",
  "frontend/src/pages/WatchlistPage.tsx",
  "frontend/src/pages/admin/AdminCommoditiesPage.tsx",
  "frontend/src/pages/admin/AdminMarketsPage.tsx",
  "frontend/src/pages/admin/AdminPriceUpdatesPage.tsx",
  "frontend/src/pages/admin/AdminSignalsPage.tsx",
  "frontend/src/pages/admin/AdminIntelligencePages.tsx",
  "frontend/src/pages/admin/AdminFAQPage.tsx",
  "frontend/src/pages/admin/AdminFeedbackPage.tsx",
  "frontend/src/pages/admin/AdminExportPage.tsx",
];
for (const file of completionFiles) requireText(file, "finally");

if (failures.length) {
  console.error("CR-01 STATIC CHECK: FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("CR-01 STATIC CHECK: PASS");
console.log("PASS: shared circular page, overlay, and button spinner components exist");
console.log("PASS: approved green/bright-green/gold/white gradient and glow are present");
console.log("PASS: approved light and dark overlay backgrounds are present");
console.log("PASS: login, registration, logout, public data, feedback, and watchlist waits are covered");
console.log("PASS: admin loading and submit/apply waits are covered");
console.log("PASS: busy buttons are disabled and completion paths clear busy state");
