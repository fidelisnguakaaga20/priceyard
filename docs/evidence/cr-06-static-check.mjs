import { readFileSync } from "node:fs";

const login = readFileSync("frontend/src/pages/LoginPage.tsx", "utf8");
const register = readFileSync("frontend/src/pages/RegisterPage.tsx", "utf8");
const styles = readFileSync("frontend/src/styles.css", "utf8");
const pkg = readFileSync("frontend/package.json", "utf8");

function expect(value, label) {
  if (!value) {
    console.error("CR-06 STATIC CHECK: FAIL");
    console.error("- " + label);
    process.exit(1);
  }
  console.log("PASS: " + label);
}

for (const [name, source, id] of [
  ["login", login, "login-password"],
  ["register", register, "register-password"],
]) {
  expect(source.includes("const [showPassword, setShowPassword] = useState(false)"), name + " is hidden by default");
  expect(source.includes('type={showPassword ? "text" : "password"}'), name + " toggles only the input presentation type");
  expect(source.includes('type="button"'), name + " visibility control cannot submit the form");
  expect(source.includes("aria-pressed={showPassword}"), name + " exposes toggle state accessibly");
  expect(source.includes('aria-controls="' + id + '"'), name + " control targets its password input");
  expect(source.includes('aria-label={showPassword ? "Hide password" : "Show password"}'), name + " has an accessible dynamic label");
  expect(source.includes('{showPassword ? "Hide" : "Show"}'), name + " displays the approved Show/Hide text");
}

expect(styles.includes(".password-field"), "shared password-field layout exists");
expect(styles.includes(".password-toggle"), "shared password-toggle styling exists");
expect(styles.includes(".password-toggle:focus-visible"), "keyboard focus is visible");
expect(styles.includes("padding-right: 76px"), "input text stays clear of the toggle");
expect(!pkg.includes("lucide") && !pkg.includes("fortawesome") && !pkg.includes("heroicons"), "no icon/UI dependency was added");

console.log("CR-06 STATIC CHECK: PASS");
