# Definition of Done

> Code existing isn't the same as done (master §92). Use the right list for the level you're closing.

## Work package → `DONE`

```text
[ ] Scope in SPEC completed; out-of-scope respected
[ ] Only owned paths touched (CODEOWNERS clean)
[ ] Contract exists/updated for anything another module sees (API, event, tool, ML IO) + example
[ ] Unit tests for domain logic; contract tests for produced interfaces
[ ] Errors use the common error envelope; no silent failures
[ ] Structured logging with request_id/site_id/event_id (+ operator/machine/model_version where relevant); no secrets
[ ] Mock still available (for consumers' tests) and in sync with the contract
[ ] Local startup verified (`make up`, your module's compose file)
[ ] STATUS.md updated (WP → DONE, log line); catalogs rows updated (status column)
[ ] Merged to develop via reviewed PR, CI green
```

## Module → `DONE`

```text
[ ] All WPs DONE (or explicitly cut and recorded in STATUS + SPEC)
[ ] Acceptance criteria in SPEC all ticked
[ ] Integration checklist in SPEC all ticked
[ ] Every consumer switched from mock to real (or has a dated plan)
[ ] Demo path involving this module verified at the relevant gate
[ ] SPEC reflects what was actually built (refined scope, future extensions updated)
```

## Contract change → merged

```text
[ ] Schema + example updated; version bumped correctly (additive = minor, breaking = new major side by side)
[ ] Catalog row(s) updated
[ ] Producer conformance test passes
[ ] For breaking: contract_change issue open, consumers listed, deprecation window stated
[ ] Owner + at least one consumer approved the PR
```

## Safety-relevant change (anything touching M04 rules, alert paths, or safety tools) → merged

```text
[ ] Deterministic behavior tested with explicit cases (incl. stale/invalid sensor data)
[ ] Offline edge behavior unchanged or improved (offline test run)
[ ] No path allows the cloud/UI/LLM to suppress an edge rule without a versioned rule change
[ ] Reviewed by the M04 owner
```
