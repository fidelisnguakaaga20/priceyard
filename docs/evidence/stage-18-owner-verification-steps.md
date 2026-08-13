# Stage 18 Owner Verification

Stage 18 adds the React + TypeScript public/user frontend. It has no database migration.

## 1. Copy the backend environment

```bash
cp ~/Downloads/priceyard-stage17/priceyard/backend/.env ~/Downloads/priceyard-stage18/priceyard/backend/.env
```

## 2. Run the automated build/API/route smoke

From the project root:

```bash
cd ~/Downloads/priceyard-stage18/priceyard
python docs/evidence/stage-18-owner-smoke.py
```

Expected final automated line:

```text
STAGE 18 OWNER SMOKE: PASS
```

The smoke deliberately does not depend on headless Chrome screenshots. Repeated Windows Chrome runs were nondeterministic even while the page and API were healthy. Visual browser/mobile proof remains mandatory in Step 3 and must be supplied manually before Stage 18 approval.

## 3. Required manual interaction check

Keep the backend and frontend running in two terminals if needed:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

```bash
cd frontend
npm run dev
```

Open `http://127.0.0.1:5173` and verify:

- Home, Prices, Commodity Detail, Price History, Market Days and FAQ render.
- Register creates a normal account and logs in.
- Login works and Dashboard shows the access label.
- Watchlist can save and remove an item.
- Feedback can submit a 1–5 rating.
- Guest/free views do not display full premium intelligence; trial/active paid/admin may view it when backend access permits.
- Possible Meaning and Suggested Action are visible and described as non-guaranteed guidance.
- The required price, market-signal and storage disclaimers are shown where relevant.
- At a narrow/mobile browser width the page remains usable without clipped controls or unreadable content.

Send the automated terminal output and confirm the manual items above before Stage 18 is approved. Stage 19 must not start before that approval.


## 4. Integration-fix retest

After the approved registration/mobile integration fixes, use the latest Stage 18 integration-fixed folder. Start backend and frontend, then verify:

- Register a new unique user: the browser must receive a successful registration response, not 500.
- Log in with that new user.
- Open Watchlist at an iPhone SE / 375px-style viewport and confirm the introductory paragraph, filters, cards and buttons fit without horizontal clipping.
- Watchlist add/remove and feedback already produced owner 201/204/201 evidence, but may be spot-checked again.
- Transient Supabase DNS/pooler failures must not be mistaken for frontend layout defects; if connectivity drops, confirm `verify_database_connection()` and retry.

Stage 19 remains blocked until the owner confirms registration and mobile visual PASS and approves Stage 18.


## Latest second-mobile-fix retest
The owner can open Commodity Detail directly at `/commodities/Egusi`. When the latest approved Egusi price card exists, the Prices page also exposes the `View intelligence →` link. A missing current approved Egusi record may render the page with an empty-state message; the route itself must still render normally.

After starting the latest backend/frontend, verify at iPhone SE 375x667 that there is no horizontal panning: header, access strip, Watchlist heading/description, form, saved item card, Remove button and footer must all stay within the viewport.
