# PY-07 browser session storage - owner decision required

Current browser sign-in keeps its bearer secret in localStorage (Remember me) or
sessionStorage. Server revocation/reset and existing logout safeguards are already
verified, but scripts running on the page can read these stored secrets. No claim
of complete session safety is justified while that exposure remains.

Recommended local-only scope:
- Move browser login secrets to HttpOnly cookies; JavaScript cannot read the
  bearer secret. Require Secure cookies outside the literal isolated loopback
  test context. Keep existing bearer authentication for API clients.
- Preserve the existing90-day maximum token lifetime and Remember me control.
  Remembered login survives browser closure until expiry/revocation. Unremembered
  login uses a browser-session cookie. Tabs in the same browser profile share the
  browser login/logout; this differs from the current tab-scoped sessionStorage
  behavior and is the specific owner-policy decision being requested.
- Keep original login/registration/Google/reset screens and business access.
  Existing valid stored browser logins may be exchanged only after server
  validation, preserving their remaining lifetime; then remove the browser-stored
  secret. If safe conversion is impossible, stop for review instead of silently
  extending access or deleting credentials. No token/secret in logs or URLs.
- Add origin checks, anti-forgery protection for cookie-authenticated writes,
  precise credentialed CORS allowlists and account-change/stale-response safety.
  Cookie-authenticated logout must revoke the server token and remove the cookie.
  Offline logout clears the device's view immediately; server revocation cannot
  be promised without connectivity. Do not invent a shorter subscription/session.
- No database fields, dependencies, production configuration, provider connection,
  migration or deployment. Test hostile origins/CSRF, existing bearer clients,
  login/reset/logout/Remember me/account switching and private cache boundaries
  synthetically, including native revocation and browser checks.

Tradeoffs: tabs share one browser identity; cookie restrictions can affect hosted
frontend/backend on different sites. Same-site hosting/reverse-proxy compatibility
must be verified under PY-35 before release. Cookies reduce secret extraction;
they do not make injected scripts harmless or guarantee remote offline revocation.

Decision: owner answered "Approve protected browser sessions" on2026-10-18.
Only this local scope is authorized; live hosting/cookie/CORS verification is PY-35
and remains outside permission. No production connection/configuration change.
