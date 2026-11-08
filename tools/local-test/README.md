# Local test harness

| File | Purpose |
|---|---|
| `guard.py` | Runs every backend test (`backend/tests`) inside an isolated process: no network, no DNS, no child processes, no real configuration, only a fresh in-memory SQLite database. CI runs this before every deploy. |
| `build_frontend.py` | Rebuilds the website in a throwaway copy with network access blocked. Used by `backend/tests/test_local_build_recovery.py`. |
| `node_guard.cjs` | Blocks network and file access for Node.js processes started by `build_frontend.py`. |
| `render_build_checks.mjs` | Checks the website's real build settings (Vite configuration) in that throwaway copy. Called by `build_frontend.py`. |

Run all backend tests:

```
python -I -B tools/local-test/guard.py
```

Run a subset with `--pattern`, for example `--pattern "test_payment*.py"`.
Result files go to `tools/local-test/runtime/`, which git ignores.

Older one-off scripts and their result records are in [`archive/local-test`](../../archive/local-test).
