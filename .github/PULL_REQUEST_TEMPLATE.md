## Workstream / work package / area

- Workstream: `MXX — name` · WP: `MXX-WPn — title`
- Ownership area: A / B / C / D / E (docs/architecture/REPOSITORY_STRUCTURE.md §6)
- Branch type: feature / contract / fix / refactor / docs

## What changed

<!-- 2–5 bullets -->

## Contract changes

- [ ] None
- [ ] Additive: list files (regenerated with `python scripts/dev.py contracts`)
- [ ] Breaking: link the `contract_change` issue; list consumers and deprecation window

## Tests

<!-- commands run + results; `python scripts/dev.py check` for structural changes -->

## Screenshots / demo (UI or demo-path changes)

## Checklist

- [ ] Only my ownership area changed (shared paths: reviewed by area A + affected area)
- [ ] No new folders without real code; no new top-level folder without an ADR
- [ ] Layer rules respected (thin routes, other capabilities via service/schemas, Copilot via services, frontend via API only)
- [ ] Workstream Status section updated (WP state + Update log line)
- [ ] Catalog rows updated if an API/event/table/tool changed
- [ ] Safety logic stays deterministic; Copilot facts come from tools (if relevant)
- [ ] Meets `docs/development/DEFINITION_OF_DONE.md` for the WP (or state what's left)
