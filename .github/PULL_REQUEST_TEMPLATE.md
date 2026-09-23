## Module / work package

- Module: `MXX — name`
- WP: `MXX-WPn — title`
- Branch type: feature / contract / fix / docs

## What changed

<!-- 2–5 bullets -->

## Contract changes

- [ ] None
- [ ] Additive (minor bump): list files + new version
- [ ] Breaking: link the `contract_change` issue; list consumers and deprecation window

## Dependencies

- Uses mocks for:
- Unblocks:

## Tests

<!-- commands run + results -->

## Screenshots / demo (UI or demo-path changes)

## Checklist

- [ ] Only paths owned by my module (or my delegated slot) are changed
- [ ] No imports of other modules' internals (only `public.py`, `backend/core`, contracts, generated client)
- [ ] Module `STATUS.md` updated in this PR (WP state + Update log line)
- [ ] Catalog rows updated if an API/event/table/tool changed
- [ ] Safety logic stays deterministic; Copilot facts come from tools (if relevant)
- [ ] Meets `docs/04-workflow/DEFINITION_OF_DONE.md` for the WP (or state what's left)
