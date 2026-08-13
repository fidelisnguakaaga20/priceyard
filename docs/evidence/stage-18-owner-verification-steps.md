# Stage 18 Owner Verification

Stage 18 adds the React + TypeScript public/user frontend. It has no database migration.

## 1. Copy the backend environment

```bash
cp ~/Downloads/priceyard-stage17/priceyard/backend/.env ~/Downloads/priceyard-stage18/priceyard/backend/.env
```

## 2. Run the automated build/browser smoke

From the project root:

```bash
cd ~/Downloads/priceyard-stage18/priceyard
python docs/evidence/stage-18-owner-smoke.py
```

Expected final automated line:

```text
STAGE 18 OWNER SMOKE: PASS
```

The script also creates `docs/evidence/stage-18-owner-mobile.png` using a 390x844 Chrome window.

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
