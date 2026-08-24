# CR-01 Browser Verification

## Automated browser status

The cloud browser could not access the local Vite preview. Navigation to `http://127.0.0.1:4173` was blocked with `ERR_BLOCKED_BY_CLIENT` by the browser security boundary. The browser instructions prohibit bypassing that boundary or switching to an alternate browser-control surface.

This is recorded as an environment limitation, not as visual proof. Production compilation and focused source checks pass, but owner-side visual interaction remains required before CR-01 receives final visual approval.

## Owner visual checklist

1. Run the frontend and backend using the existing project READMEs.
2. Confirm login, registration, and logout show the circular button spinner and block a repeated click.
3. Confirm Dashboard/account checks use the page overlay spinner.
4. Confirm Home approved prices, Prices search, Price History, FAQ, market days, and commodity detail show data loaders.
5. Confirm feedback submission and watchlist save/remove actions show button spinners.
6. Confirm admin data pages show data loaders and admin submit/apply actions show disabled button spinners.
7. Trigger one successful request and one failed request; confirm every spinner clears in both cases.
8. At a phone-width viewport, confirm loader labels remain readable and do not cause horizontal overflow.
9. Confirm the spinner uses green, bright green, gold, and white with a soft glow.
10. Confirm light/dark full-page overlays use the approved translucent backgrounds.

