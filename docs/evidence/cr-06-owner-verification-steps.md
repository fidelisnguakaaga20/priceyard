# CR-06 Owner Verification Steps

CR-06 is not owner-approved until these steps pass.

## 1. Pull and run the focused check

From the PriceYard repository root:

```bash
git pull origin master
node docs/evidence/cr-06-static-check.mjs
```

Expected final line:

```text
CR-06 STATIC CHECK: PASS
```

## 2. Build the frontend

```bash
cd frontend
npm run build
```

Expected: TypeScript and Vite build complete without errors.

## 3. Start PriceYard

Backend terminal:

```bash
cd ~/Downloads/priceyard-stage20-assessment/priceyard/backend
python -m uvicorn app.main:app --reload
```

Frontend terminal:

```bash
cd ~/Downloads/priceyard-stage20-assessment/priceyard/frontend
npm run dev
```

## 4. Browser checks

Login:

1. Open Login.
2. Confirm the password is hidden initially.
3. Type a password.
4. Select Show: the same password becomes visible.
5. Select Hide: the same password becomes hidden.
6. Confirm Show/Hide does not submit the form.
7. Confirm correct login still shows its spinner, success popup, and redirect.
8. Confirm wrong login still shows only the error popup.

Register:

1. Open Register.
2. Confirm the password is hidden initially.
3. Type a password.
4. Select Show and Hide; confirm the value does not change.
5. Confirm Show/Hide does not submit the form.
6. Confirm registration still shows its spinner, success popup, and redirect.

Mobile/narrow view:

- Confirm the toggle stays inside the field.
- Confirm password text does not overlap the toggle.
- Confirm the control is easy to tap and keyboard focus is visible.

## Approval gate

Send the static-check output, production-build output, and browser result. Do not approve or start any next stage until these pass.
