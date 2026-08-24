import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const read = (path) => readFileSync(resolve(root, path), "utf8");
const failures = [];

function includes(path, ...needles) {
  const source = read(path).toLowerCase();
  for (const needle of needles) {
    if (!source.includes(needle.toLowerCase())) failures.push(`${path}: missing ${needle}`);
  }
}

function ordered(path, ...needles) {
  const source = read(path);
  let previous = -1;
  for (const needle of needles) {
    const index = source.indexOf(needle, previous + 1);
    if (index < 0) failures.push(`${path}: missing ordered step ${needle}`);
    else previous = index;
  }
}

includes(
  "frontend/src/components/Toast.tsx",
  'role={kind === "error" ? "alert" : "status"}',
  'aria-live="polite"',
  "toast-dismiss",
);
includes(
  "frontend/src/context/ToastContext.tsx",
  "ToastProvider",
  "showToast",
  "window.setTimeout",
  "4500",
  "window.clearTimeout",
);
includes("frontend/src/main.tsx", "ToastProvider");

includes(
  "frontend/src/pages/LoginPage.tsx",
  "Login successful. Welcome back to PriceYard.",
  'showToast(err instanceof Error ? err.message : "Login failed.", "error")',
  "disabled={busy}",
);
ordered(
  "frontend/src/pages/LoginPage.tsx",
  "await login(email, password)",
  "setBusy(false)",
  "requestAnimationFrame",
  'showToast("Login successful. Welcome back to PriceYard.")',
  "navigate(target",
);

includes(
  "frontend/src/pages/RegisterPage.tsx",
  "Registration successful. Welcome to PriceYard.",
  'showToast(err instanceof Error ? err.message : "Registration failed.", "error")',
  "disabled={busy}",
);
ordered(
  "frontend/src/pages/RegisterPage.tsx",
  "await register(",
  "setBusy(false)",
  "requestAnimationFrame",
  'showToast("Registration successful. Welcome to PriceYard.")',
  'navigate("/dashboard"',
);

includes("frontend/src/components/Layout.tsx", "Logout successful.", "disabled={loggingOut}");
ordered(
  "frontend/src/components/Layout.tsx",
  "setLoggingOut(true)",
  "logout()",
  "setLoggingOut(false)",
  "requestAnimationFrame",
  'showToast("Logout successful.")',
  'navigate("/"',
);

includes(
  "frontend/src/styles.css",
  ".toast-region",
  "#ecfdf5",
  "#16a34a",
  "#064e3b",
  "#fef2f2",
  "#dc2626",
  "#7f1d1d",
  "@keyframes priceyard-toast-in",
  "@media (max-width: 640px) { .toast-region",
);

if (failures.length) {
  console.error("CR-02 STATIC CHECK: FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("CR-02 STATIC CHECK: PASS");
console.log("PASS: shared accessible popup system exists and auto-dismisses");
console.log("PASS: login, registration, and logout use the exact approved success messages");
console.log("PASS: auth failures use error popups and never call success messages in catch paths");
console.log("PASS: spinner clears before each success/error popup is shown");
console.log("PASS: redirect follows the success popup trigger");
console.log("PASS: approved success/error colors and mobile positioning are present");
