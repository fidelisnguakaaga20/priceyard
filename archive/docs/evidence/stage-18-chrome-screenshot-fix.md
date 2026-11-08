# Stage 18 browser verification helper fix

Owner retest on Windows proved the production frontend build, FastAPI health,
Vite API proxy, frontend dev server, and `/price-updates` API all worked, but
Chrome `--dump-dom` did not exit within 45 seconds.

Approved smallest fix: verification helper only. Browser route proof now uses
headless Chrome screenshots. If Chrome writes the screenshot but leaves a
background process alive, the helper terminates that process and validates the
non-empty screenshot artifact. The application, APIs, database, dependencies,
and Stage 19 scope are unchanged.
