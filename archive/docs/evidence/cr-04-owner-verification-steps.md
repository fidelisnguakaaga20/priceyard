# CR-04 Owner Verification Steps

CR-04 is verification-only. Do not delete or edit approved Egusi/Kwali records during the browser check.

## 1. Pull the CR-04 evidence helper

```bash
cd ~/Downloads/priceyard-stage20-assessment/priceyard
git pull origin master
```

## 2. Run focused source checks

```bash
node docs/evidence/cr-01-static-check.mjs
node docs/evidence/cr-02-static-check.mjs
python docs/evidence/cr-03-static-check.py
python -m py_compile docs/evidence/cr-04-owner-regression.py
```

Expected final lines include:

```text
CR-01 STATIC CHECK: PASS
CR-02 STATIC CHECK: PASS
CR-03 STATIC CHECK: PASS
```

## 3. Run the frontend production build

```bash
cd ~/Downloads/priceyard-stage20-assessment/priceyard/frontend
npm run build
```

Expected: TypeScript and Vite build complete successfully.

## 4. Run configured PostgreSQL/API regression

```bash
cd ~/Downloads/priceyard-stage20-assessment/priceyard/backend
python ../docs/evidence/cr-04-owner-regression.py fidelisnguakaaga20@gmail.com
```

The password prompt does not display typed characters. Never send the password or `.env` contents.

Expected final line:

```text
CR-04 OWNER REGRESSION: PASS
```

The helper creates only uniquely named temporary records and removes them. Approved audit evidence remains. It prints each phase/PASS immediately and limits new PostgreSQL connection attempts to 15 seconds; if it stops, return the last displayed CHECK/PASS line.

## 5. Read-only browser verification

Start backend and frontend in separate terminals, then confirm without clicking Delete:

1. Registration, login and logout show the approved spinner followed by the correct popup.
2. Wrong login shows only the red error popup.
3. Dashboard and admin data loaders spin and stop normally.
4. Public commodity/market filters show only Egusi and Kwali Market.
5. Public prices/history contain no inactive commodity or market.
6. Admin Commodities shows Egusi active and Beans/Palm oil inactive.
7. Admin Markets shows Kwali active and the other approved markets inactive.
8. Admin management pages load; CRUD is already tested safely by the regression helper.
9. Feedback submission still works.
10. Mobile-width spinner/popup display remains clean.

Return the source-check output, build result, final regression line and browser result. CR-05 remains blocked until CR-04 owner approval.
