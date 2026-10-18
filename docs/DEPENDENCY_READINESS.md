# PY-35 dependency release gate — 2026-10-18

This is a targeted remaining-readiness check, not a repeated application audit.
Before owner approval, no package was changed. The approved exact updates below
were subsequently installed only in the isolated snapshot. No live PriceYard
service was contacted. Public advisories were read separately from isolated tests.

Before this batch the application declared Vite5.4.11/react-router-dom6.28.0 and
had no tracked frontend lockfile. It now declares Vite6.4.4/router6.30.6 with a
reviewed lockfile. Backend requirements still use ranges. Installed test tools
alone do not prove a reproducible or advisory-free hosted build.

Confirmed version matches, with exposure distinguished from package presence:

- [Vite GHSA-vg6x-rcgg-rjx6](https://github.com/vitejs/vite/security/advisories/GHSA-vg6x-rcgg-rjx6)
  includes5.4.11 and concerns the development server, including loopback use.
  Our synthetic preview serves compiled files through Python and never starts
  Vite's HTTP/dev server. Static production files are a different exposure path.
- [Vite GHSA-fx2h-pf6j-xcff](https://github.com/vitejs/vite/security/advisories/GHSA-fx2h-pf6j-xcff)
  covers Windows development-server file-denial bypass under its stated network/
  filesystem conditions. Do not start the old development server to reproduce it.
- [Vite GHSA-rq7h-c2jc-7f22](https://github.com/vitejs/vite/security/advisories/GHSA-rq7h-c2jc-7f22)
  lists6.4.4 as its patched6.x release. An old5.4.x patch is not a current blanket fix.
- [Router GHSA-9jcx-v3wj-wh4m](https://github.com/remix-run/react-router/security/advisories/GHSA-9jcx-v3wj-wh4m)
  includes6.28.0; exploitation depends on passing untrusted navigation paths.
  This is a conditional application risk, not evidence of an actual account attack.
- [Router GHSA-jjmj-jmhj-qwj2](https://github.com/remix-run/react-router/security/advisories/GHSA-jjmj-jmhj-qwj2)
  lists6.30.6 as the patched6.x release for a later redirect issue. Do not upgrade
  only to6.30.2 and assume all later advisories are resolved.
- [GHSA-2w69-qvjg-hvjx](https://github.com/remix-run/react-router/security/advisories/GHSA-2w69-qvjg-hvjx)
  explicitly excludes declarative BrowserRouter applications from that particular
  loader/action redirect issue. Do not label all router advisories exploitable here.

Approved isolated follow-up: owner answered "do best option" on2026-10-18 to
the exact Vite6.4.4/router6.30.6 exception proposed in this document. This lifts
the earlier no-install boundary only for this isolated security-update scope:
fetch exact Vite6.4.4 and react-router-dom6.30.6 from the official npm registry,
verify downloaded package integrity, disable package lifecycle scripts, prepare a
reviewed lockfile, and check the existing plugin/React/Node compatibility before
changing declarations. No automatic major framework redesign or React migration.
Keep old tools intact; never silently reuse the old build for changed dependencies.
Repeat TypeScript/build, routing/auth/account/CSV/history/mobile/14-card browser
checks on the new dependency set. Roll back only the new isolated dependency
snapshot if validation fails; preserve source/history and prior evidence.

Also capture exact backend installed versions and resolve reproducible constraints
in an isolated environment before release; refresh primary advisories for every
resolved direct/transitive package. This short review is not a complete CVE scan,
an advisory-free certificate or permission to upload code to a scanning service.

No production deployment is approved. Even a successful local upgrade would not
close hosting/provider/backup-restore checks in OPERATIONAL_READINESS.md.

Batch82 results:official-registry-only lock123 resolved entries;73 applicable
packages installed in the fixed isolated snapshot, package lifecycle scripts
disabled. Existing React18.3.1/plugin4.3.4/TypeScript5.6.3 retained; plugin's declared
peer range includes Vite6. TypeScript/Vite6.4.4 build104 modules passed4.65s. Five
build-recovery tests pass. Original CSS source is unchanged; compiler formatting
differs, but computed layout/typography agree with the old build at1366/375px.
Ten session tests, seven baseline workflows,14 dashboard cards, payment recovery,
CSV, original price editing, fake Google and251-row history pass. See batch82
evidence. Old dependency trees/build remain intact; use the marked55446 preview,
not an old root node_modules tree or an application-configured development server.
The lockfile has package integrity hashes; npm ci checked downloaded archives.
Linux hosting/browser support and a complete current dependency/advisory review
remain separate release checks, not claims inferred from this Windows fixture.
