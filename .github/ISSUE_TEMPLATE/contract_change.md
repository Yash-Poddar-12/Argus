---
name: Breaking contract change
about: Propose a breaking change to an API, event, schema, tool, or ML interface
title: "contract(MXX): <what changes>"
labels: contract-change
---

**Producer module:** MXX
**Contract file(s):** `contracts/...`
**Current version → new version:** v1 → v2

## What changes and why

## Compatibility plan

- [ ] New version added side by side (v1 still served/emitted)
- Deprecation window: until gate G_ / date

## Consumers (from EVENT_CATALOG / API_CATALOG / TOOL_AND_ML_CONTRACTS). Tick when migrated

- [ ] MYY (@owner)
- [ ] MZZ (@owner)

## Removal of old version

- [ ] All consumers ticked
- [ ] Old version removed; catalogs updated
