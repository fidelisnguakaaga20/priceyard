# CR-04 Owner Browser/Runtime Verification

Date: 2026-08-24  
Result: RETESTED/PASS

## Evidence observed

The owner started FastAPI with:

```text
python -m uvicorn app.main:app --reload
```

Observed runtime results:

| Area | Evidence | Result |
|---|---|---|
| Backend startup | Application startup complete | PASS |
| Public prices | Repeated `GET /price-updates` → `200 OK` | PASS |
| Registration | `POST /auth/register` → `201 Created` | PASS |
| Correct login | `POST /auth/login` → `200 OK` | PASS |
| Wrong login | Intentional `POST /auth/login` → `401 Unauthorized` | PASS |
| Profile/account | `GET /auth/me` → `200 OK` | PASS |
| Trial/subscription | `GET /subscriptions/{user_id}` → `200 OK` | PASS |
| Active public catalogs | `GET /commodities` and `GET /markets` → `200 OK` | PASS |
| Focused prices | Egusi + Kwali Market filtered request → `200 OK` | PASS |
| Admin reads | Users, subscriptions, all commodities/markets, price history, feedback summary → `200 OK` | PASS |
| Watchlist | `GET /watchlist` → `200 OK` | PASS |

## Visual evidence already approved

- CR-01: the owner confirmed clicked actions displayed the stylish spinner.
- CR-02: the owner explicitly confirmed login, error, registration, and logout popups worked.
- CR-03: public active data and admin expansion behavior passed the owner smoke and final database query.
- The final runtime session produced no unexpected server error and no delete request.

## Conclusion

CR-04 is RETESTED/PASS. The single `401 Unauthorized` is expected negative-test evidence, not a defect. The owner's instruction to continue if the output was okay authorizes CR-05 documentation only.
