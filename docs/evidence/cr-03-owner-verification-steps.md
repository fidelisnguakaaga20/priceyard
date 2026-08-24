# CR-03 Owner Verification Steps

CR-03 cannot receive final PASS until the real configured PostgreSQL migration and owner smoke test pass.

## 1. Pull and stop local servers

Stop the running frontend/backend with `Ctrl+C`, then:

```bash
cd ~/Downloads/priceyard-stage20-assessment/priceyard
git pull origin master
```

## 2. Apply the approved data migration

```bash
cd backend
python -m alembic upgrade head
python -m alembic current
```

Expected current revision:

```text
0006_cr03_egusi_kwali (head)
```

## 3. Run the owner smoke test

Replace the placeholder with an existing PriceYard admin email. The script prompts for the admin password without displaying it. Do not send the password or `.env` contents to ChatGPT.

```bash
python ../docs/evidence/cr-03-owner-smoke.py YOUR_ADMIN_EMAIL
```

Expected final line:

```text
CR-03 OWNER SMOKE: PASS
```

The test verifies exact database/public focus, protected admin all-record views, existing auth/subscription behavior, non-admin blocking, commodity/market add-deactivate-reactivate-cleanup, Egusi/Kwali price creation and cleanup, and final Egusi/Kwali-only public state. Temporary test records are cleaned up; approved audit logs remain.

## 4. Browser check

Restart the backend and frontend. Confirm:

1. Public Prices commodity filter contains only Egusi.
2. Public Prices market filter contains only Kwali Market.
3. Public price cards/history show no inactive commodity or market.
4. Admin Commodities and Markets pages still show inactive records and allow add/edit/reactivate.
5. Login, subscription access, spinner, and auth popups still work.

Return the migration output, final smoke-test line, and browser result without secrets.

