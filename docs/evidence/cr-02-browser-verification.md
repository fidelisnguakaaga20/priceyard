# CR-02 Owner Browser Verification

Status: REQUIRED before CR-02 final approval.

The cloud browser cannot access the local Vite address because of the previously recorded local-address security boundary. Production build and focused source/compiled-artifact checks pass; the owner must complete this short interaction check.

## Checklist

1. Correct login: spinner appears, then closes; green success popup says `Login successful. Welcome back to PriceYard.`; dashboard/target page loads.
2. Wrong login: spinner appears, then closes; red error popup appears; no success popup appears.
3. Correct registration with a new email: spinner appears, then closes; green success popup says `Registration successful. Welcome to PriceYard.`; dashboard loads.
4. Duplicate-email registration: spinner appears, then closes; red error popup appears; no success popup appears.
5. Logout: spinner appears, then closes; green success popup says `Logout successful.`; public home page loads.
6. Confirm the popup disappears automatically after about 4.5 seconds and can also be dismissed with the `×` button.
7. At phone width, confirm the popup stays inside the screen and the message remains readable.
8. Confirm success styling is pale green/white with green accent and dark-green text; error styling is pale red/white with red accent and dark-red text.

