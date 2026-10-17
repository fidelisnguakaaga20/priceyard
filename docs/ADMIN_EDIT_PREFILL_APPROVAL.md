# Existing Admin editing safeguard — approved for local implementation

Owner approved on2026-10-17: "Approve the editing safeguard". Implement and verify
in batches of one or two original forms; no production authorization is implied.

Scope: PY-27, local development and synthetic testing only. Existing forms for
Market signals, Quality signals, Buying zones, Sell-watch windows, Storage
suitability and Cost breakdowns accept an ID to edit but do not load that record's
saved values. Submitting a manually reconstructed form sends blank optional fields
as null (and blank costs as zero), potentially replacing existing saved details.

Proposed behavior: entering a known ID loads that record into the same existing
fields using the authorized Admin list already fetched. Editing and explicitly
clearing fields then continue through the existing PATCH endpoint. Switching to
another known ID replaces unsaved form values with that record's saved values.
Clearing the ID restores the original new-record defaults. Unknown IDs must not
silently submit values loaded for a different ID; show the existing error style.

No new screen, buttons, database/form fields, commodity measurements, grades,
subscription rules, public wording or layout. No historical-record repair,
automatic saves, production connections or production migration. Existing field
validation, access and atomic audit requirements remain. Browser tests must prove
saved optional details/costs survive changing one field and reloading, and confirm
explicit clearing, ID switching, unknown IDs and original creation still work.

This specific approval covers loading/replacing values in existing editing forms.
It does not approve new fields, screens, business rules or production changes.
